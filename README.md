# Feature Detective 🔍

웹 크롤링을 통한 경쟁사 기능 분석 및 리포트 생성 도구

## 📋 프로젝트 개요

Feature Detective는 웹사이트를 크롤링하여 특정 기능의 지원 여부를 자동으로 분석하고, 경쟁사 비교 리포트를 생성하는 도구입니다. 키워드 기반의 NLP 분석을 통해 O/X/△ 판별을 수행하며, PDF 및 CSV 형태의 상세한 리포트를 제공합니다.

## ✨ 주요 기능

- **📁 프로젝트 관리**: 경쟁사 분석 프로젝트 생성 및 관리
- **🔑 키워드 관리**: CSV 업로드/다운로드 지원
- **🕷️ 웹 크롤링**: Beautiful Soup 기반 스마트 크롤링
- **🤖 AI 분석**: NLP 기반 기능 지원 여부 판별 (O/X/△)
- **📊 시각화**: 경쟁사별 기능 매트릭스 및 차트
- **📄 리포트 생성**: PDF/CSV 형태의 상세 분석 리포트
- **⚡ 비동기 처리**: Celery 기반 백그라운드 작업

## 🏗️ 기술 스택

### Backend

- **Flask**: Python 웹 프레임워크
- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 메시지 브로커 및 캐싱
- **Celery**: 비동기 작업 처리
- **Beautiful Soup**: 웹 스크래핑
- **SQLAlchemy**: ORM

### Frontend

- **React**: 사용자 인터페이스
- **TypeScript**: 타입 안전성
- **Material-UI**: UI 컴포넌트 라이브러리
- **Axios**: HTTP 클라이언트

### DevOps

- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 컨테이너 오케스트레이션

## 🚀 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- Git

### 설치 및 실행

1. **저장소 클론**

   ```bash
   git clone <repository-url>
   cd featureDetective
   ```

2. **환경 변수 설정**

   ```bash
   cp env.example .env
   # .env 파일을 편집하여 필요한 설정값 입력
   ```

3. **Docker Compose로 실행**

   ```bash
   docker-compose up -d
   ```

4. **애플리케이션 접속**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 📁 프로젝트 구조

```
featureDetective/
├── backend/                 # Flask 백엔드
│   ├── app.py              # 메인 애플리케이션
│   ├── config.py           # 설정 관리
│   ├── models/             # 데이터베이스 모델
│   ├── routes/             # API 엔드포인트
│   ├── services/           # 비즈니스 로직
│   ├── tasks/              # Celery 태스크
│   └── requirements.txt    # Python 의존성
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # UI 컴포넌트
│   │   ├── pages/          # 페이지
│   │   ├── services/       # API 클라이언트
│   │   └── contexts/       # React Context
│   └── package.json        # Node 의존성
├── celeryconfig.py         # Celery 설정
├── docker-compose.yml      # Docker Compose 설정
└── README.md
```

## 🔧 개발 환경 설정

### 로컬 개발

1. **Backend 설정**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```

2. **Frontend 설정**

   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **데이터베이스 설정**
   ```bash
   # PostgreSQL 및 Redis 실행
   docker-compose up postgres redis -d
   ```

## 📚 API 문서

### 프로젝트 관리

- `GET /api/projects` - 프로젝트 목록 조회
- `POST /api/projects` - 프로젝트 생성
- `GET /api/projects/{id}` - 프로젝트 상세 조회
- `PUT /api/projects/{id}` - 프로젝트 수정
- `DELETE /api/projects/{id}` - 프로젝트 삭제

### 키워드 관리

- `GET /api/projects/{id}/keywords` - 키워드 목록 조회
- `POST /api/projects/{id}/keywords` - 키워드 추가
- `PUT /api/keywords/{id}` - 키워드 수정
- `DELETE /api/keywords/{id}` - 키워드 삭제
- `POST /api/projects/{id}/keywords/upload` - CSV 업로드

### 크롤링

- `POST /api/projects/{id}/crawl` - 크롤링 시작
- `GET /api/projects/{id}/crawl/status` - 크롤링 상태 조회
- `GET /api/projects/{id}/results` - 크롤링 결과 조회

### 리포트

- `GET /api/projects/{id}/report/pdf` - PDF 리포트 생성
- `GET /api/projects/{id}/report/csv` - CSV 리포트 생성

## 🧪 테스트

### Backend 테스트

```bash
cd backend
python -m pytest
```

### Frontend 테스트

```bash
cd frontend
npm test
```

## 📦 배포

### Docker 배포

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 환경 변수

프로덕션 환경에서는 다음 환경 변수를 설정하세요:

- `DATABASE_URL`: PostgreSQL 연결 문자열
- `REDIS_URL`: Redis 연결 문자열
- `SECRET_KEY`: Flask 시크릿 키
- `CELERY_BROKER_URL`: Celery 브로커 URL

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/your-repo/issues)
- **문서**: [Wiki](https://github.com/your-repo/wiki)
- **이메일**: support@featuredetective.com

## 🗺️ 로드맵

- [ ] 실시간 크롤링 진행률 표시
- [ ] 고급 필터링 및 검색 기능
- [ ] 팀 협업 기능
- [ ] API 레이트 리미팅
- [ ] 모바일 앱 지원
- [ ] 다국어 지원

---

**Feature Detective** - 경쟁사 분석을 더욱 스마트하게! 🚀
