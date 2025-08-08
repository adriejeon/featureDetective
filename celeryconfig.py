# Celery 설정
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# 태스크 설정
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'Asia/Seoul'
enable_utc = True

# 워커 설정
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000

# 태스크 라우팅
task_routes = {
    'tasks.crawling_tasks.*': {'queue': 'crawling'},
    'tasks.analysis_tasks.*': {'queue': 'analysis'},
}

# 태스크 결과 설정
task_ignore_result = False
task_store_errors_even_if_ignored = True

# 로깅 설정
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
