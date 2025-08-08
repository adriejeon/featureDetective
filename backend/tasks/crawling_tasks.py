from celery import Celery
from services.crawling_service import CrawlingService
from models.crawling_result import CrawlingResult, db
import time

# Celery 앱 설정
celery = Celery('feature_detective')

@celery.task(bind=True)
def crawl_urls_task(self, project_id, urls):
    """URL 목록 크롤링 Celery 태스크"""
    try:
        crawling_service = CrawlingService()
        results = []
        
        for i, url in enumerate(urls):
            try:
                # 진행률 업데이트
                progress = int((i / len(urls)) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': progress,
                        'total': 100,
                        'status': f'{i+1}/{len(urls)} URL 크롤링 중: {url}'
                    }
                )
                
                # URL 크롤링 실행
                result = crawling_service.crawl_url(url, project_id)
                results.append({
                    'url': url,
                    'status': 'success',
                    'result': result.to_dict()
                })
                
                # 요청 간 딜레이 (서버 부하 방지)
                time.sleep(2)
                
            except Exception as e:
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
        
        # 완료
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100,
                'total': 100,
                'status': '크롤링 완료',
                'results': results
            }
        )
        
        return {
            'status': 'success',
            'results': results,
            'message': f'{len(urls)}개 URL의 크롤링이 완료되었습니다.'
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'error',
            'error': str(e),
            'message': '크롤링 중 오류가 발생했습니다.'
        }

@celery.task(bind=True)
def crawl_url_task(self, project_id, url):
    """단일 URL 크롤링 Celery 태스크"""
    try:
        # 태스크 상태 업데이트
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': '크롤링 시작...'}
        )
        
        # 크롤링 서비스 초기화
        crawling_service = CrawlingService()
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': '웹페이지 접속 중...'}
        )
        
        # URL 크롤링 실행
        result = crawling_service.crawl_url(url, project_id)
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': '키워드 분석 중...'}
        )
        
        # 완료
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': '크롤링 완료'}
        )
        
        return {
            'status': 'success',
            'result': result.to_dict(),
            'message': f'{url} 크롤링이 완료되었습니다.'
        }
        
    except Exception as e:
        # 에러 처리
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'error',
            'error': str(e),
            'message': f'{url} 크롤링 중 오류가 발생했습니다.'
        }

@celery.task
def analyze_keywords_task(project_id, url, text_content):
    """키워드 분석 Celery 태스크"""
    try:
        crawling_service = CrawlingService()
        crawling_service._analyze_keywords(project_id, url, text_content)
        
        return {
            'status': 'success',
            'message': '키워드 분석이 완료되었습니다.'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': '키워드 분석 중 오류가 발생했습니다.'
        }

@celery.task
def batch_crawl_task(project_id, urls):
    """배치 크롤링 Celery 태스크"""
    try:
        crawling_service = CrawlingService()
        results = []
        
        for i, url in enumerate(urls):
            try:
                result = crawling_service.crawl_url(url, project_id)
                results.append({
                    'url': url,
                    'status': 'success',
                    'result': result.to_dict()
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
            
            # 요청 간 딜레이
            time.sleep(1)
        
        return {
            'status': 'success',
            'results': results,
            'message': f'{len(urls)}개 URL의 배치 크롤링이 완료되었습니다.'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': '배치 크롤링 중 오류가 발생했습니다.'
        }
