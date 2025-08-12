import logging
from typing import List, Dict, Any
from models.crawling_result import CrawlingResult, db
from models.keyword import Keyword
from models.feature_analysis import FeatureAnalysis
from models.ai_analysis import AIAnalysis, ExtractedFeature
from crawlers.help_doc_crawler import HelpDocCrawler
from crawlers.content_extractor import ContentExtractor
from services.vertex_ai_service import VertexAIService

logger = logging.getLogger(__name__)


class CrawlingService:
    """크롤링 서비스 클래스 - 새로운 크롤러 모듈 사용"""
    
    def __init__(self):
        """크롤링 서비스 초기화"""
        self.crawler = HelpDocCrawler(rate_limit=1.0, max_depth=2, max_pages=50)
        self.content_extractor = ContentExtractor()
        
        # Vertex AI 서비스 초기화 (선택적)
        try:
            self.vertex_ai = VertexAIService()
            self.ai_enabled = True
            logger.info("Vertex AI 서비스가 활성화되었습니다.")
        except Exception as e:
            self.vertex_ai = None
            self.ai_enabled = False
            logger.warning(f"Vertex AI 서비스를 초기화할 수 없습니다: {e}")
    
    def crawl_url(self, url: str, project_id: int) -> CrawlingResult:
        """
        단일 URL 크롤링 및 분석
        
        Args:
            url: 크롤링할 URL
            project_id: 프로젝트 ID
            
        Returns:
            CrawlingResult 객체
        """
        crawling_result = None
        try:
            # 크롤링 결과 생성
            crawling_result = CrawlingResult()
            crawling_result.project_id = project_id
            crawling_result.url = url
            crawling_result.status = 'processing'
            db.session.add(crawling_result)
            db.session.commit()
            
            logger.info(f"Starting crawl for URL: {url}")
            
            # 새로운 크롤러로 크롤링
            crawl_data = self.crawler.crawl(url)
            
            if crawl_data.get('error'):
                raise Exception(crawl_data['error'])
            
            # 크롤링 결과 업데이트
            crawling_result.content = crawl_data.get('content', '')
            crawling_result.status = 'completed'
            crawling_result.metadata = crawl_data.get('metadata', {})
            crawling_result.content_length = crawl_data.get('content_length', 0)
            crawling_result.extraction_method = crawl_data.get('extraction_method', '')
            db.session.commit()
            
            logger.info(f"Successfully crawled: {url}")
            
            # 키워드 분석
            self._analyze_keywords(project_id, url, crawl_data.get('content', ''))
            
            # AI 분석 (활성화된 경우)
            if self.ai_enabled and crawl_data.get('content'):
                self._perform_ai_analysis(project_id, crawling_result.id, crawl_data)
            
            return crawling_result
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            # 에러 처리
            if crawling_result:
                crawling_result.status = 'failed'
                crawling_result.error_message = str(e)
                db.session.commit()
            
            raise e
    
    def crawl_multiple_urls(self, urls: List[str], project_id: int) -> List[CrawlingResult]:
        """
        여러 URL 크롤링
        
        Args:
            urls: 크롤링할 URL 리스트
            project_id: 프로젝트 ID
            
        Returns:
            CrawlingResult 객체 리스트
        """
        results = []
        
        for url in urls:
            try:
                result = self.crawl_url(url, project_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                # 실패한 경우에도 결과 객체 생성
                failed_result = CrawlingResult()
                failed_result.project_id = project_id
                failed_result.url = url
                failed_result.status = 'failed'
                failed_result.error_message = str(e)
                db.session.add(failed_result)
                results.append(failed_result)
        
        db.session.commit()
        return results
    
    def crawl_site(self, base_url: str, project_id: int, follow_links: bool = True) -> List[CrawlingResult]:
        """
        전체 사이트 크롤링
        
        Args:
            base_url: 크롤링할 사이트의 기본 URL
            project_id: 프로젝트 ID
            follow_links: 내부 링크 따라가기 여부
            
        Returns:
            CrawlingResult 객체 리스트
        """
        logger.info(f"Starting site crawl: {base_url}")
        
        try:
            # 사이트 크롤링
            crawl_data_list = self.crawler.crawl_site(base_url, follow_links=follow_links)
            
            results = []
            for crawl_data in crawl_data_list:
                try:
                    # 크롤링 결과 저장
                    crawling_result = CrawlingResult()
                    crawling_result.project_id = project_id
                    crawling_result.url = crawl_data.get('url', '')
                    crawling_result.content = crawl_data.get('content', '')
                    crawling_result.status = 'completed'
                    crawling_result.metadata = crawl_data.get('metadata', {})
                    crawling_result.content_length = crawl_data.get('content_length', 0)
                    crawling_result.extraction_method = crawl_data.get('extraction_method', '')
                    
                    db.session.add(crawling_result)
                    results.append(crawling_result)
                    
                    # 키워드 분석
                    self._analyze_keywords(project_id, crawl_data.get('url', ''), crawl_data.get('content', ''))
                    
                except Exception as e:
                    logger.error(f"Error processing crawl data: {e}")
            
            db.session.commit()
            logger.info(f"Site crawl completed. Processed {len(results)} pages.")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during site crawl: {e}")
            raise e
    
    def _analyze_keywords(self, project_id: int, url: str, text_content: str):
        """
        키워드 분석 및 기능 지원 여부 판별
        
        Args:
            project_id: 프로젝트 ID
            url: 분석한 URL
            text_content: 분석할 텍스트 내용
        """
        # 프로젝트의 키워드 조회
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        
        for keyword in keywords:
            try:
                # 키워드 매칭 및 분석
                support_status, confidence_score, matched_text = self._analyze_keyword_support(
                    keyword.keyword, text_content
                )
                
                # 분석 결과 저장
                analysis = FeatureAnalysis()
                analysis.project_id = project_id
                analysis.keyword_id = keyword.id
                analysis.url = url
                analysis.support_status = support_status
                analysis.confidence_score = confidence_score
                analysis.matched_text = matched_text
                
                db.session.add(analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing keyword {keyword.keyword}: {e}")
        
        db.session.commit()
    
    def _analyze_keyword_support(self, keyword: str, text_content: str) -> tuple:
        """
        키워드 지원 여부 분석
        
        Args:
            keyword: 분석할 키워드
            text_content: 분석할 텍스트
            
        Returns:
            (support_status, confidence_score, matched_text) 튜플
        """
        # 텍스트 전처리
        text_lower = text_content.lower()
        keyword_lower = keyword.lower()
        
        # 직접 매칭 (정확한 키워드)
        if keyword_lower in text_lower:
            return 'O', 0.9, keyword
        
        # 부분 매칭 (키워드의 일부가 포함된 경우)
        keyword_words = keyword_lower.split()
        if len(keyword_words) > 1:
            matched_words = [word for word in keyword_words if word in text_lower]
            if len(matched_words) >= len(keyword_words) * 0.7:
                return '△', 0.7, ', '.join(matched_words)
        
        # 유사 키워드 매칭
        similar_keywords = self._find_similar_keywords(keyword_lower, text_lower)
        if similar_keywords:
            return '△', 0.6, ', '.join(similar_keywords[:3])
        
        # 부정 키워드 확인
        negative_indicators = [
            '지원하지 않음', '불가능', '제한', '없음', '미지원', 
            'not supported', 'unavailable', 'not available', 'limited'
        ]
        for indicator in negative_indicators:
            if indicator in text_lower:
                return 'X', 0.8, indicator
        
        # 기본값: 미지원
        return 'X', 0.5, ''
    
    def _find_similar_keywords(self, keyword: str, text: str) -> List[str]:
        """
        유사 키워드 찾기
        
        Args:
            keyword: 찾을 키워드
            text: 검색할 텍스트
            
        Returns:
            유사한 키워드 리스트
        """
        # 키워드를 단어로 분리
        keyword_words = set(keyword.split())
        
        # 텍스트에서 유사한 단어 찾기
        text_words = set(text.split())
        
        # 공통 단어 찾기
        common_words = keyword_words.intersection(text_words)
        
        if len(common_words) >= len(keyword_words) * 0.5:
            return list(common_words)
        
        return []
    
    def get_crawling_status(self, project_id: int) -> tuple:
        """
        크롤링 상태 조회
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            (status_summary, results) 튜플
        """
        results = CrawlingResult.query.filter_by(project_id=project_id).all()
        
        status_summary = {
            'total': len(results),
            'completed': len([r for r in results if r.status == 'completed']),
            'processing': len([r for r in results if r.status == 'processing']),
            'failed': len([r for r in results if r.status == 'failed']),
            'pending': len([r for r in results if r.status == 'pending'])
        }
        
        return status_summary, results
    
    def get_crawl_stats(self) -> Dict[str, Any]:
        """
        크롤링 통계 조회
        
        Returns:
            크롤링 통계 딕셔너리
        """
        return self.crawler.get_crawl_stats()
    
    def _perform_ai_analysis(self, project_id: int, crawling_result_id: int, crawl_data: Dict[str, Any]):
        """
        AI 분석 수행
        
        Args:
            project_id: 프로젝트 ID
            crawling_result_id: 크롤링 결과 ID
            crawl_data: 크롤링 데이터
        """
        try:
            if not self.ai_enabled or not self.vertex_ai:
                return
            
            content = crawl_data.get('content', '')
            if not content:
                return
            
            # 회사명 추출 (URL에서 도메인 추출)
            from urllib.parse import urlparse
            domain = urlparse(crawl_data.get('url', '')).netloc
            company_name = domain.replace('www.', '').split('.')[0] if domain else 'Unknown'
            
            logger.info(f"AI 분석 시작: {company_name}")
            
            # 1. 기능 추출 분석
            feature_analysis = self.vertex_ai.extract_features_from_text(company_name, content)
            
            # AI 분석 결과 저장
            ai_analysis = AIAnalysis()
            ai_analysis.project_id = project_id
            ai_analysis.crawling_result_id = crawling_result_id
            ai_analysis.analysis_type = 'feature_extraction'
            ai_analysis.analysis_data = feature_analysis
            
            db.session.add(ai_analysis)
            db.session.flush()  # ID 생성
            
            # 추출된 기능들을 개별 테이블에 저장
            extracted_features = feature_analysis.get('extracted_features', [])
            for feature_data in extracted_features:
                feature = ExtractedFeature()
                feature.ai_analysis_id = ai_analysis.id
                feature.feature_name = feature_data.get('name', '')
                feature.category = feature_data.get('category', '')
                feature.description = feature_data.get('description', '')
                feature.confidence_score = feature_data.get('confidence', 0.0)
                
                db.session.add(feature)
            
            db.session.commit()
            logger.info(f"AI 기능 추출 완료: {len(extracted_features)}개 기능")
            
        except Exception as e:
            logger.error(f"AI 분석 중 오류: {e}")
            db.session.rollback()
    
    def analyze_keyword_with_ai(self, project_id: int, keyword: str, content: str) -> Dict[str, Any]:
        """
        AI를 사용한 키워드 분석
        
        Args:
            project_id: 프로젝트 ID
            keyword: 분석할 키워드
            content: 분석할 콘텐츠
            
        Returns:
            AI 분석 결과
        """
        try:
            if not self.ai_enabled or not self.vertex_ai:
                return {
                    'support_status': 'X',
                    'confidence_score': 0.0,
                    'matched_text': '',
                    'analysis_reason': 'AI 서비스가 비활성화되어 있습니다.'
                }
            
            result = self.vertex_ai.analyze_keyword_support(keyword, content)
            logger.info(f"AI 키워드 분석 완료: {keyword} - {result.get('support_status')}")
            
            return result
            
        except Exception as e:
            logger.error(f"AI 키워드 분석 중 오류: {e}")
            return {
                'support_status': 'X',
                'confidence_score': 0.0,
                'matched_text': '',
                'analysis_reason': f'AI 분석 오류: {str(e)}'
            }
    
    def compare_products_with_ai(self, project_id: int, product1_name: str, product1_features: List[Dict],
                                product2_name: str, product2_features: List[Dict]) -> Dict[str, Any]:
        """
        AI를 사용한 제품 비교 분석
        
        Args:
            project_id: 프로젝트 ID
            product1_name: 첫 번째 제품명
            product1_features: 첫 번째 제품의 기능 리스트
            product2_name: 두 번째 제품명
            product2_features: 두 번째 제품의 기능 리스트
            
        Returns:
            비교 분석 결과
        """
        try:
            if not self.ai_enabled or not self.vertex_ai:
                return {
                    'comparison_summary': {},
                    'feature_comparison': [],
                    'competitive_analysis': {
                        'error': 'AI 서비스가 비활성화되어 있습니다.'
                    }
                }
            
            result = self.vertex_ai.compare_products(
                product1_name, product1_features,
                product2_name, product2_features
            )
            
            # 결과를 데이터베이스에 저장
            comparison = ProductComparison()
            comparison.project_id = project_id
            comparison.product1_name = product1_name
            comparison.product2_name = product2_name
            comparison.comparison_data = result
            
            db.session.add(comparison)
            db.session.commit()
            
            logger.info(f"AI 제품 비교 분석 완료: {product1_name} vs {product2_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"AI 제품 비교 분석 중 오류: {e}")
            db.session.rollback()
            return {
                'comparison_summary': {},
                'feature_comparison': [],
                'competitive_analysis': {
                    'error': f'AI 분석 오류: {str(e)}'
                }
            }
    
    def close(self):
        """크롤러 리소스 정리"""
        self.crawler.close()
