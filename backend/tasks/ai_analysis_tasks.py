"""
AI 분석 Celery 태스크
"""

from celery import Celery
from services.crawling_service import CrawlingService
from services.vertex_ai_service import VertexAIService
from models.ai_analysis import AIAnalysis, ExtractedFeature, ProductComparison, db
from models.crawling_result import CrawlingResult
import logging

logger = logging.getLogger(__name__)

# Celery 앱 설정
celery = Celery('feature_detective')

@celery.task(bind=True)
def analyze_crawled_content_task(self, project_id, crawling_result_id):
    """크롤링된 콘텐츠에 AI 분석 수행 태스크"""
    try:
        logger.info(f"AI 분석 태스크 시작: 프로젝트 {project_id}, 크롤링 결과 {crawling_result_id}")
        
        # 태스크 상태 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': 'AI 분석 초기화 중...'
            }
        )
        
        # 크롤링 결과 조회
        crawling_result = CrawlingResult.query.get(crawling_result_id)
        if not crawling_result:
            raise Exception(f"크롤링 결과를 찾을 수 없습니다: {crawling_result_id}")
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 20,
                'total': 100,
                'status': 'Vertex AI 서비스 초기화 중...'
            }
        )
        
        # Vertex AI 서비스 초기화
        vertex_ai = VertexAIService()
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 40,
                'total': 100,
                'status': '기능 추출 분석 중...'
            }
        )
        
        # 회사명 추출
        from urllib.parse import urlparse
        domain = urlparse(crawling_result.url).netloc
        company_name = domain.replace('www.', '').split('.')[0] if domain else 'Unknown'
        
        # 기능 추출 분석
        feature_analysis = vertex_ai.extract_features_from_text(company_name, crawling_result.content)
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 80,
                'total': 100,
                'status': '분석 결과 저장 중...'
            }
        )
        
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
        
        # 완료
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100,
                'total': 100,
                'status': 'AI 분석 완료'
            }
        )
        
        logger.info(f"AI 분석 완료: {len(extracted_features)}개 기능 추출")
        
        return {
            'status': 'success',
            'message': f'{len(extracted_features)}개 기능이 추출되었습니다.',
            'extracted_features_count': len(extracted_features),
            'analysis_id': ai_analysis.id
        }
        
    except Exception as e:
        logger.error(f"AI 분석 태스크 오류: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'error',
            'error': str(e),
            'message': 'AI 분석 중 오류가 발생했습니다.'
        }

@celery.task(bind=True)
def analyze_keyword_with_ai_task(self, project_id, keyword, content):
    """AI를 사용한 키워드 분석 태스크"""
    try:
        logger.info(f"AI 키워드 분석 태스크 시작: {keyword}")
        
        # 태스크 상태 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': 'AI 키워드 분석 시작...'
            }
        )
        
        # Vertex AI 서비스 초기화
        vertex_ai = VertexAIService()
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 50,
                'total': 100,
                'status': '키워드 분석 중...'
            }
        )
        
        # 키워드 분석 수행
        result = vertex_ai.analyze_keyword_support(keyword, content)
        
        # 완료
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100,
                'total': 100,
                'status': '키워드 분석 완료'
            }
        )
        
        logger.info(f"AI 키워드 분석 완료: {keyword} - {result.get('support_status')}")
        
        return {
            'status': 'success',
            'keyword': keyword,
            'analysis_result': result
        }
        
    except Exception as e:
        logger.error(f"AI 키워드 분석 태스크 오류: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'error',
            'error': str(e),
            'message': 'AI 키워드 분석 중 오류가 발생했습니다.'
        }

@celery.task(bind=True)
def compare_products_with_ai_task(self, project_id, product1_name, product1_features, 
                                 product2_name, product2_features):
    """AI를 사용한 제품 비교 분석 태스크"""
    try:
        logger.info(f"AI 제품 비교 분석 태스크 시작: {product1_name} vs {product2_name}")
        
        # 태스크 상태 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '제품 비교 분석 시작...'
            }
        )
        
        # Vertex AI 서비스 초기화
        vertex_ai = VertexAIService()
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 50,
                'total': 100,
                'status': '제품 기능 비교 분석 중...'
            }
        )
        
        # 제품 비교 분석 수행
        result = vertex_ai.compare_products(
            product1_name, product1_features,
            product2_name, product2_features
        )
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 80,
                'total': 100,
                'status': '분석 결과 저장 중...'
            }
        )
        
        # 결과를 데이터베이스에 저장
        comparison = ProductComparison()
        comparison.project_id = project_id
        comparison.product1_name = product1_name
        comparison.product2_name = product2_name
        comparison.comparison_data = result
        
        db.session.add(comparison)
        db.session.commit()
        
        # 완료
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100,
                'total': 100,
                'status': '제품 비교 분석 완료'
            }
        )
        
        logger.info(f"AI 제품 비교 분석 완료: {product1_name} vs {product2_name}")
        
        return {
            'status': 'success',
            'message': '제품 비교 분석이 완료되었습니다.',
            'comparison_result': result,
            'comparison_id': comparison.id
        }
        
    except Exception as e:
        logger.error(f"AI 제품 비교 분석 태스크 오류: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'error',
            'error': str(e),
            'message': 'AI 제품 비교 분석 중 오류가 발생했습니다.'
        }

@celery.task(bind=True)
def batch_ai_analysis_task(self, project_id, crawling_result_ids):
    """배치 AI 분석 태스크"""
    try:
        logger.info(f"배치 AI 분석 태스크 시작: 프로젝트 {project_id}, {len(crawling_result_ids)}개 결과")
        
        results = []
        
        for i, crawling_result_id in enumerate(crawling_result_ids):
            try:
                # 진행률 업데이트
                progress = int((i / len(crawling_result_ids)) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': progress,
                        'total': 100,
                        'status': f'{i+1}/{len(crawling_result_ids)} 분석 중...'
                    }
                )
                
                # 개별 분석 수행
                result = analyze_crawled_content_task.delay(project_id, crawling_result_id)
                results.append({
                    'crawling_result_id': crawling_result_id,
                    'task_id': result.id,
                    'status': 'started'
                })
                
            except Exception as e:
                logger.error(f"배치 분석 중 오류 (결과 ID {crawling_result_id}): {e}")
                results.append({
                    'crawling_result_id': crawling_result_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        # 완료
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100,
                'total': 100,
                'status': '배치 AI 분석 완료'
            }
        )
        
        return {
            'status': 'success',
            'message': f'{len(crawling_result_ids)}개 결과에 대한 배치 AI 분석이 시작되었습니다.',
            'results': results
        }
        
    except Exception as e:
        logger.error(f"배치 AI 분석 태스크 오류: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'error',
            'error': str(e),
            'message': '배치 AI 분석 중 오류가 발생했습니다.'
        }
