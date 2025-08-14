# Feature Detective

Vertex AI를 활용한 지능형 기능 탐지 및 분석 도구

## 🚀 새로운 기능 (v2.0)

### 완전 비동기 Job 시스템

- **실시간 진행률 추적**: 웹소켓을 통한 실시간 진행률 업데이트
- **Job 상태 관리**: pending → running → completed/failed 상태 추적
- **취소 및 재시도**: 실행 중인 Job 취소 및 실패한 Job 재시도 기능
- **Vertex AI 2.5 Pro**: 최신 Gemini 2.5 Pro 모델 사용

### 실시간 진행률 표시

- 웹소켓 연결 상태 표시
- 단계별 진행률 바 (크롤링 → AI 분석 → 비교 분석)
- 현재 실행 중인 단계 표시
- 완료/실패 상태 알림

## 🏗️ 아키텍처

```
프론트엔드 (React) ←→ 웹소켓 (포트 5004) ←→ 백엔드 (Flask, 포트 5003)
                                    ↓
                              Celery + Redis (Job Queue)
                                    ↓
                              Vertex AI (Gemini 2.5 Pro)
```

## 📦 설치 및 실행

### 1. 백엔드 설정

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Redis 서버 실행

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis

# Windows
# Redis for Windows 다운로드 후 실행
```

### 3. Celery 워커 실행

```bash
cd backend
celery -A celeryconfig worker --loglevel=info
```

### 4. 백엔드 서버 실행

```bash
cd backend
python run.py  # Flask 서버 (포트 5003)
```

### 5. 웹소켓 서버 실행

```bash
cd backend
python run_websocket.py  # 웹소켓 서버 (포트 5004)
```

### 6. 프론트엔드 실행

```bash
cd frontend
npm install
npm start  # React 앱 (포트 3000)
```

## 🔧 환경 변수 설정

`.env` 파일을 생성하고 다음 설정을 추가:

```env
# Google Cloud
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=global
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 📊 데이터 흐름

### 완전 비동기 처리 흐름

1. **사용자 입력** → POST `/api/feature-detection/detect-features`
2. **Job 생성** → 상태: `pending`, 진행률: 0%
3. **Celery 태스크 시작** → 상태: `running`
4. **실시간 진행률 업데이트**:
   - 5%: 서비스 초기화
   - 15-40%: 웹사이트 크롤링 (URL별 진행률)
   - 45-80%: Vertex AI 기능 분석 (제품별 진행률)
   - 85-95%: 기능 병합 및 비교 분석
   - 100%: 완료
5. **웹소켓으로 실시간 알림** → 프론트엔드 업데이트
6. **결과 저장** → 데이터베이스에 분석 결과 저장

### Job 상태 관리

- **pending**: 대기 중
- **running**: 실행 중 (진행률 0-100%)
- **completed**: 완료 (진행률 100%)
- **failed**: 실패 (오류 메시지 포함)
- **cancelled**: 취소됨

## 🎯 주요 기능

### 1. 실시간 진행률 추적

- 웹소켓을 통한 실시간 진행률 업데이트
- 단계별 상세 진행 상황 표시
- 연결 상태 실시간 모니터링

### 2. Job 관리

- Job 상태 조회: `GET /api/jobs/{job_id}`
- Job 취소: `POST /api/jobs/{job_id}/cancel`
- Job 재시도: `POST /api/jobs/{job_id}/retry`
- 프로젝트별 Job 목록: `GET /api/projects/{project_id}/jobs`

### 3. Vertex AI 2.5 Pro 통합

- 최신 Gemini 2.5 Pro 모델 사용
- 향상된 기능 추출 정확도
- 더 정교한 비교 분석

### 4. 웹소켓 이벤트

- `job_progress`: 진행률 업데이트
- `job_completed`: 작업 완료
- `job_failed`: 작업 실패
- `connected`: 웹소켓 연결
- `joined_job`: Job 구독
- `left_job`: Job 구독 해제

## 🔍 API 엔드포인트

### 기능 탐지

- `POST /api/feature-detection/detect-features` - 비동기 기능 탐지 시작
- `GET /api/jobs/{job_id}` - Job 상태 조회

### Job 관리

- `GET /api/projects/{project_id}/jobs` - 프로젝트 Job 목록
- `POST /api/jobs/{job_id}/cancel` - Job 취소
- `POST /api/jobs/{job_id}/retry` - Job 재시도

## 🎨 UI/UX 개선사항

### 실시간 진행률 표시

- 웹소켓 연결 상태 인디케이터
- 단계별 진행률 바
- 현재 실행 중인 단계 텍스트
- 상태별 색상 구분 (대기/실행/완료/실패)

### 반응형 디자인

- 모바일 친화적 레이아웃
- 실시간 업데이트 애니메이션
- 직관적인 상태 표시

## 🚀 성능 최적화

### 비동기 처리

- Celery를 통한 백그라운드 작업 처리
- Redis를 통한 Job 큐 관리
- 웹소켓을 통한 실시간 통신

### 메모리 효율성

- 대용량 데이터 스트리밍 처리
- 중간 결과 캐싱
- 자동 리소스 정리

## 🔧 개발 도구

### 디버깅

- Celery 워커 로그 모니터링
- 웹소켓 연결 상태 확인
- Job 상태 실시간 추적

### 테스트

- 단위 테스트: `pytest`
- 통합 테스트: API 엔드포인트 테스트
- 웹소켓 테스트: 실시간 통신 테스트

## 📈 모니터링

### 로그 추적

- Job 실행 로그
- 웹소켓 연결 로그
- 오류 및 예외 처리

### 성능 메트릭

- 처리 시간 측정
- 메모리 사용량 모니터링
- 동시 처리 Job 수 추적

## 🔮 향후 계획

- [ ] 대시보드 추가 (Job 히스토리, 통계)
- [ ] 배치 처리 기능
- [ ] 알림 시스템 (이메일, 슬랙)
- [ ] 고급 분석 기능
- [ ] API 문서화 (Swagger)

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.

---

**Feature Detective v2.0** - 완전 비동기 Job 시스템과 실시간 진행률 추적으로 더욱 강력해진 기능 탐지 도구
