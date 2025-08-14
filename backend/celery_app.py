from celery import Celery
import sys
import os

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Celery 앱 생성
celery_app = Celery('feature_detective')

# 설정 적용
celery_app.config_from_object('celeryconfig')

# 태스크 수동 등록
celery_app.autodiscover_tasks(['tasks'], force=True)

# 태스크 수동 import
try:
    import tasks.feature_detection_tasks
    import tasks.crawling_tasks
    import tasks.ai_analysis_tasks
    print("모든 태스크 모듈이 성공적으로 로드되었습니다.")
except Exception as e:
    print(f"태스크 로드 중 오류: {e}")

if __name__ == '__main__':
    celery_app.start()
