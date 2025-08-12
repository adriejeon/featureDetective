"""
고급 크롤링 서비스
Intercom과 같은 고급 크롤링 기능을 제공하는 서비스
"""

import logging
from typing import List, Dict, Any, Optional
from models.crawling_result import CrawlingResult, db
from models.keyword import Keyword
from models.feature_analysis import FeatureAnalysis
from models.ai_analysis import AIAnalysis, ExtractedFeature
from crawlers.advanced_site_crawler import AdvancedSiteCrawler, CrawlConfig
from crawlers.apify_crawler import ApifyAdvancedCrawler, ApifyCrawlConfig, run_apify_crawler
from services.vertex_ai_service import VertexAIService
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AdvancedCrawlingService:
    """고급 크롤링 서비스 클래스"""
    
    def __init__(self):
        """고급 크롤링 서비스 초기화"""
        # 기본 설정
        self.default_config = CrawlConfig(
            max_pages=50,
            max_depth=3,
            rate_limit=1.0,
            timeout=30,
            follow_subdomains=True,
            use_sitemap=True,
            respect_robots_txt=True
        )
        
        # Vertex AI 서비스 초기화
        try:
            self.vertex_ai = VertexAIService()
            self.ai_enabled = True
            logger.info("Vertex AI 서비스가 활성화되었습니다.")
        except Exception as e:
            self.vertex_ai = None
            self.ai_enabled = False
            logger.warning(f"Vertex AI 서비스를 초기화할 수 없습니다: {e}")
    
    def create_custom_config(self, **kwargs) -> CrawlConfig:
        """
        사용자 정의 크롤링 설정 생성
        
        Args:
            **kwargs: 설정 옵션들
            
        Returns:
            CrawlConfig 객체
        """
        config = CrawlConfig()
        
        # 기본값 복사
        for key, value in self.default_config.__dict__.items():
            setattr(config, key, value)
        
        # 사용자 정의 값으로 덮어쓰기
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def crawl_site_advanced(self, base_url: str, project_id: int, 
                           config: CrawlConfig = None) -> List[CrawlingResult]:
        """
        고급 사이트 크롤링
        
        Args:
            base_url: 크롤링할 기본 URL
            project_id: 프로젝트 ID
            config: 크롤링 설정 (None이면 기본 설정 사용)
            
        Returns:
            CrawlingResult 객체 리스트
        """
        logger.info(f"고급 사이트 크롤링 시작: {base_url}")
        
        if config is None:
            config = self.default_config
        
        # 크롤러 초기화
        crawler = AdvancedSiteCrawler(config)
        
        try:
            # 크롤링 실행
            crawl_results = crawler.crawl(base_url)
            
            # 데이터베이스에 결과 저장
            db_results = []
            for result in crawl_results:
                try:
                    # 크롤링 결과 저장
                    crawling_result = CrawlingResult()
                    crawling_result.project_id = project_id
                    crawling_result.url = result['url']
                    crawling_result.content = result['content']
                    crawling_result.status = 'completed'
                    crawling_result.metadata = {
                        'title': result['title'],
                        'depth': result['depth'],
                        'source': result['source'],
                        'content_length': result['content_length'],
                        'status_code': result['status_code'],
                        'crawl_config': config.__dict__
                    }
                    crawling_result.content_length = result['content_length']
                    crawling_result.extraction_method = 'advanced_site_crawler'
                    
                    db.session.add(crawling_result)
                    db_results.append(crawling_result)
                    
                    # 키워드 분석
                    self._analyze_keywords(project_id, result['url'], result['content'])
                    
                    # AI 분석 (활성화된 경우)
                    if self.ai_enabled and result['content']:
                        self._perform_ai_analysis(project_id, crawling_result.id, result)
                    
                except Exception as e:
                    logger.error(f"결과 저장 중 오류 ({result['url']}): {e}")
                    continue
            
            db.session.commit()
            
            # 크롤링 통계 로깅
            stats = crawler.get_crawl_stats()
            logger.info(f"크롤링 완료: {len(db_results)}개 페이지 저장")
            logger.info(f"크롤링 통계: {stats}")
            
            return db_results
            
        except Exception as e:
            logger.error(f"고급 크롤링 중 오류: {e}")
            db.session.rollback()
            raise e
        finally:
            crawler.close()
    
    def crawl_with_custom_settings(self, base_url: str, project_id: int, 
                                  include_patterns: List[str] = None,
                                  exclude_patterns: List[str] = None,
                                  css_exclude_selectors: List[str] = None,
                                  max_pages: int = 50,
                                  max_depth: int = 3) -> List[CrawlingResult]:
        """
        사용자 정의 설정으로 크롤링
        
        Args:
            base_url: 크롤링할 기본 URL
            project_id: 프로젝트 ID
            include_patterns: 포함할 URL 패턴들
            exclude_patterns: 제외할 URL 패턴들
            css_exclude_selectors: 제외할 CSS 선택자들
            max_pages: 최대 페이지 수
            max_depth: 최대 깊이
            
        Returns:
            CrawlingResult 객체 리스트
        """
        config = self.create_custom_config(
            max_pages=max_pages,
            max_depth=max_depth,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            css_exclude_selectors=css_exclude_selectors
        )
        
        return self.crawl_site_advanced(base_url, project_id, config)
    
    def crawl_help_center(self, base_url: str, project_id: int) -> List[CrawlingResult]:
        """
        헬프 센터 전용 크롤링 (Apify 기반)
        
        Args:
            base_url: 헬프 센터 URL
            project_id: 프로젝트 ID
            
        Returns:
            CrawlingResult 객체 리스트
        """
        logger.info(f"헬프 센터 크롤링 시작 (Apify): {base_url}")
        
        # 헬프 센터 전용 설정
        config = ApifyCrawlConfig(
            max_pages=100,
            max_depth=4,
            include_patterns=[
                '*/help/*', '*/support/*', '*/docs/*', '*/guide/*',
                '*/manual/*', '*/tutorial/*', '*/faq/*', '*/knowledge/*'
            ],
            exclude_patterns=[
                '*.pdf', '*.doc', '*.docx', '*.zip', '*.rar',
                'mailto:', 'tel:', 'javascript:',
                '/admin/', '/login/', '/logout/', '/register/',
                '?utm_', '?fbclid', '?gclid'
            ],
            css_exclude_selectors=[
                'nav', 'footer', 'header', 'aside', 'sidebar',
                '.advertisement', '.ads', '.banner', '.popup',
                '.cookie-notice', '.newsletter', '.social-share',
                'script', 'style', 'noscript'
            ],
            css_click_selectors=[
                '.load-more', '.show-more', '.expand', '.toggle',
                '.pagination .next', '.pagination .load-more'
            ],
            css_wait_selectors=[
                '.content', '.article', '.help-content', '.documentation'
            ]
        )
        
        return self.crawl_site_with_apify(base_url, project_id, config)
    
    def crawl_documentation(self, base_url: str, project_id: int) -> List[CrawlingResult]:
        """
        문서 사이트 전용 크롤링
        
        Args:
            base_url: 문서 사이트 URL
            project_id: 프로젝트 ID
            
        Returns:
            CrawlingResult 객체 리스트
        """
        doc_config = self.create_custom_config(
            max_pages=200,
            max_depth=5,
            include_patterns=[
                '*/docs/*', '*/documentation/*', '*/api/*', '*/reference/*',
                '*/guide/*', '*/tutorial/*', '*/examples/*', '*/getting-started/*'
            ],
            exclude_patterns=[
                '*.pdf', '*.zip', '*.tar.gz',
                'mailto:', 'tel:', 'javascript:',
                '/admin/', '/login/', '/logout/',
                '?utm_', '?fbclid', '?gclid'
            ],
            css_exclude_selectors=[
                'nav', 'footer', 'header', 'aside', 'sidebar',
                '.advertisement', '.ads', '.banner', '.popup',
                '.cookie-notice', '.newsletter', '.social-share',
                'script', 'style', 'noscript'
            ]
        )
        
        return self.crawl_site_advanced(base_url, project_id, doc_config)
    
    def _analyze_keywords(self, project_id: int, url: str, text_content: str):
        """
        키워드 분석 및 기능 지원 여부 판별
        
        Args:
            project_id: 프로젝트 ID
            url: 분석한 URL
            text_content: 분석할 텍스트 내용
        """
        try:
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
                    logger.error(f"키워드 분석 중 오류 ({keyword.keyword}): {e}")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"키워드 분석 중 오류: {e}")
            db.session.rollback()
    
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
    
    def _perform_ai_analysis(self, project_id: int, crawling_result_id: int, result: Dict[str, Any]):
        """
        AI 분석 수행
        
        Args:
            project_id: 프로젝트 ID
            crawling_result_id: 크롤링 결과 ID
            result: 크롤링 결과
        """
        try:
            if not self.ai_enabled or not self.vertex_ai:
                return
            
            content = result.get('content', '')
            if not content:
                return
            
            # 회사명 추출 (URL에서 도메인 추출)
            from urllib.parse import urlparse
            domain = urlparse(result.get('url', '')).netloc
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
    
    def export_crawl_results(self, project_id: int, filepath: str, format: str = 'json'):
        """
        크롤링 결과 내보내기
        
        Args:
            project_id: 프로젝트 ID
            filepath: 저장할 파일 경로
            format: 내보내기 형식 ('json' 또는 'csv')
        """
        try:
            results = CrawlingResult.query.filter_by(project_id=project_id).all()
            
            if format.lower() == 'json':
                data = {
                    'project_id': project_id,
                    'export_time': datetime.now().isoformat(),
                    'total_results': len(results),
                    'results': [
                        {
                            'url': r.url,
                            'title': r.metadata.get('title', '') if r.metadata else '',
                            'content_length': r.content_length,
                            'status': r.status,
                            'extraction_method': r.extraction_method,
                            'created_at': r.created_at.isoformat() if r.created_at else None
                        }
                        for r in results
                    ]
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            elif format.lower() == 'csv':
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'url', 'title', 'content_length', 'status', 
                        'extraction_method', 'created_at'
                    ])
                    writer.writeheader()
                    for r in results:
                        writer.writerow({
                            'url': r.url,
                            'title': r.metadata.get('title', '') if r.metadata else '',
                            'content_length': r.content_length,
                            'status': r.status,
                            'extraction_method': r.extraction_method,
                            'created_at': r.created_at.isoformat() if r.created_at else None
                        })
            
            logger.info(f"크롤링 결과 내보내기 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"크롤링 결과 내보내기 실패: {e}")
            raise e
    
    def crawl_site_with_apify(self, base_url: str, project_id: int, config: ApifyCrawlConfig = None) -> List[CrawlingResult]:
        """
        Apify Crawlee 기반 고급 크롤링
        
        Args:
            base_url: 크롤링할 기본 URL
            project_id: 프로젝트 ID
            config: Apify 크롤링 설정
            
        Returns:
            CrawlingResult 객체 리스트
        """
        logger.info(f"Apify 크롤러로 사이트 크롤링 시작: {base_url}")
        
        try:
            # Apify 크롤러 실행
            raw_results = run_apify_crawler(base_url, project_id, config)
            
            # 결과를 CrawlingResult 객체로 변환
            crawling_results = []
            for result in raw_results:
                crawling_result = CrawlingResult(
                    project_id=result['project_id'],
                    url=result['url'],
                    content=result['content'],
                    status=result['status'],
                    error_message=result['error_message'],
                    crawled_at=datetime.utcnow(),
                    content_length=result['content_length'],
                    extraction_method=result['extraction_method'],
                    crawling_metadata=result['crawling_metadata']
                )
                crawling_results.append(crawling_result)
            
            # 데이터베이스에 저장
            for result in crawling_results:
                db.session.add(result)
            db.session.commit()
            
            # 키워드 분석 및 AI 분석 실행
            self._analyze_crawl_results(crawling_results, project_id)
            
            logger.info(f"Apify 크롤링 완료: {len(crawling_results)}개 페이지")
            return crawling_results
            
        except Exception as e:
            logger.error(f"Apify 크롤링 중 오류: {e}")
            if db.session.is_active:
                db.session.rollback()
            raise
    
    def _analyze_crawl_results(self, crawling_results: List[CrawlingResult], project_id: int):
        """
        크롤링 결과 분석 (키워드 분석 및 AI 분석)
        
        Args:
            crawling_results: 크롤링 결과 리스트
            project_id: 프로젝트 ID
        """
        logger.info(f"크롤링 결과 분석 시작: {len(crawling_results)}개 결과")
        
        try:
            # 프로젝트의 키워드 조회
            keywords = Keyword.query.filter_by(project_id=project_id).all()
            
            if not keywords:
                logger.info("분석할 키워드가 없습니다.")
                return
            
            # 각 크롤링 결과에 대해 키워드 분석 수행
            for crawling_result in crawling_results:
                if crawling_result.status != 'completed' or not crawling_result.content:
                    continue
                
                # 키워드 분석
                self._analyze_keywords_for_result(crawling_result, keywords)
                
                # AI 분석 (선택적)
                if self.ai_enabled:
                    self._perform_ai_analysis(project_id, crawling_result.id, {
                        'url': crawling_result.url,
                        'content': crawling_result.content,
                        'title': crawling_result.crawling_metadata.get('title', '') if crawling_result.crawling_metadata else ''
                    })
            
            logger.info(f"크롤링 결과 분석 완료: {len(crawling_results)}개 결과")
            
        except Exception as e:
            logger.error(f"크롤링 결과 분석 중 오류: {e}")
            if db.session.is_active:
                db.session.rollback()
    
    def _analyze_keywords_for_result(self, crawling_result: CrawlingResult, keywords: List[Keyword]):
        """
        특정 크롤링 결과에 대한 키워드 분석
        
        Args:
            crawling_result: 크롤링 결과
            keywords: 분석할 키워드 리스트
        """
        try:
            content = crawling_result.content.lower()
            
            for keyword in keywords:
                # 키워드 지원 상태 분석
                support_status, confidence, matched_text = self._analyze_keyword_support(
                    keyword.keyword, content
                )
                
                # 기존 분석 결과가 있는지 확인
                existing_analysis = FeatureAnalysis.query.filter_by(
                    crawling_result_id=crawling_result.id,
                    keyword_id=keyword.id
                ).first()
                
                if existing_analysis:
                    # 기존 결과 업데이트
                    existing_analysis.support_status = support_status
                    existing_analysis.confidence_score = confidence
                    existing_analysis.matched_text = matched_text
                    existing_analysis.updated_at = datetime.utcnow()
                else:
                    # 새로운 분석 결과 생성
                    analysis = FeatureAnalysis()
                    analysis.project_id = crawling_result.project_id
                    analysis.crawling_result_id = crawling_result.id
                    analysis.keyword_id = keyword.id
                    analysis.keyword = keyword.keyword
                    analysis.support_status = support_status
                    analysis.confidence_score = confidence
                    analysis.matched_text = matched_text
                    analysis.analysis_method = 'keyword_analysis'
                    
                    db.session.add(analysis)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"키워드 분석 중 오류: {e}")
            if db.session.is_active:
                db.session.rollback()
