# Feature Detective

경쟁사 제품의 기능 분석을 위한 웹 크롤링 및 분석 도구입니다.

## 주요 기능

### 🔍 고급 웹 크롤링 (Intercom 스타일)
- **링크 기반 탐색**: 입력된 URL을 시작점으로 하이퍼링크를 따라 자동 페이지 탐색
- **URL Globs 지원**: 와일드카드를 사용한 URL 패턴 매칭 (`*/help/*`, `*/docs/*` 등)
- **CSS 선택자 제어**: 불필요한 요소 제외 및 숨겨진 콘텐츠 클릭/대기 설정
- **XML Sitemap 활용**: robots.txt 및 sitemap.xml을 통한 빠른 페이지 발견
- **하위 도메인 탐색**: 같은 도메인의 하위 도메인 자동 탐색
- **사전 정의된 템플릿**: 헬프 센터, 문서 사이트, 이커머스 등 특화된 설정
- **스마트 콘텐츠 추출**: 네비게이션, 광고, 스크립트 등을 제거하고 깨끗한 텍스트 추출
- **속도 제한 및 재시도**: 서버 부하를 고려한 정중한 크롤링

### 🤖 AI 기반 분석
- **Vertex AI Gemini 통합**: 크롤링된 콘텐츠의 의미 분석
- **제품 기능 자동 식별**: AI가 제품 기능을 자동으로 추출
- **스마트 키워드 분석**: AI 기반 키워드 지원 여부 분석
- **제품 비교 분석**: 두 제품의 기능을 의미론적으로 비교
- **경쟁 분석 리포트**: 자동으로 경쟁 분석 리포트 생성

### 📊 키워드 기반 분석
- **키워드 매칭**: 사용자 정의 키워드로 기능 지원 여부 분석
- **신뢰도 점수**: 각 기능의 지원 확률을 점수로 제공
- **매칭된 텍스트**: 어떤 텍스트에서 키워드가 발견되었는지 표시

### 📈 리포트 생성
- **PDF 리포트**: 상세한 분석 결과를 PDF로 생성
- **CSV 내보내기**: 데이터 분석을 위한 CSV 형식 지원
- **실시간 통계**: 크롤링 진행 상황 및 분석 통계

## 기술 스택

### Backend
- **Flask**: 웹 프레임워크
- **SQLAlchemy**: ORM
- **Celery**: 비동기 작업 처리
- **Redis**: 메시지 브로커
- **BeautifulSoup4**: HTML 파싱
- **readability-lxml**: 콘텐츠 추출
- **fake-useragent**: User-Agent 랜덤화
- **Google GenAI**: Vertex AI Gemini 통합

### Frontend
- **React**: 사용자 인터페이스
- **TypeScript**: 타입 안전성
- **Material-UI**: UI 컴포넌트

## 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/feature-detective.git
cd feature-detective
```

### 2. Backend 설정
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp env.example .env
# .env 파일을 편집하여 데이터베이스 및 기타 설정을 구성
```

### 4. 데이터베이스 초기화
```bash
flask db upgrade
```

### 5. Backend 실행
```bash
# 개발 서버
python run.py

# 또는 Celery 워커 (별도 터미널에서)
celery -A tasks.crawling_tasks worker --loglevel=info
```

### 6. Frontend 설정
```bash
cd ../frontend
npm install
npm start
```

## 사용법

### 1. 프로젝트 생성
- 웹 인터페이스에서 새 프로젝트를 생성
- 프로젝트명과 설명을 입력

### 2. 키워드 추가
- 분석하고 싶은 기능들을 키워드로 추가
- 예: "API 통합", "실시간 알림", "모바일 앱" 등

### 3. 크롤링 시작
- **단일 URL 크롤링**: 특정 도움말 페이지 URL 입력
- **고급 사이트 크롤링**: Intercom 스타일의 자동 사이트 탐색
  - 헬프 센터 전용 크롤링
  - 문서 사이트 전용 크롤링
  - 사용자 정의 설정 크롤링 (URL 패턴, CSS 선택자 등)
- **배치 크롤링**: 여러 URL을 한 번에 크롤링

### 4. AI 분석 수행
- **자동 기능 추출**: 크롤링 완료 후 AI가 자동으로 제품 기능 추출
- **스마트 키워드 분석**: AI 기반 키워드 지원 여부 분석
- **제품 비교 분석**: 두 제품의 기능을 의미론적으로 비교

### 5. 분석 결과 확인
- 추출된 기능 목록 및 카테고리별 분류 확인
- 각 키워드별 AI 분석 결과 및 신뢰도 점수 확인
- 제품 비교 분석 결과 및 경쟁 우위 분석

### 6. 리포트 생성
- PDF 또는 CSV 형식으로 분석 결과 다운로드
- 프로젝트별 통계 및 요약 정보 확인

## 크롤링 모듈 구조

```
backend/
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py              # 추상 기본 크롤러
│   ├── help_doc_crawler.py          # 도움말 문서 전용 크롤러
│   ├── advanced_site_crawler.py     # 고급 사이트 크롤러 (Intercom 스타일)
│   ├── robust_crawler.py            # 강화된 웹 크롤러
│   └── content_extractor.py         # 콘텐츠 추출기
├── services/
│   ├── crawling_service.py          # 기본 크롤링 서비스
│   └── advanced_crawling_service.py # 고급 크롤링 서비스
└── utils/
    ├── __init__.py
    └── rate_limiter.py              # 요청 속도 제한
```

### 주요 클래스

#### BaseCrawler
- 모든 크롤러의 기본 클래스
- 요청 속도 제한, 재시도 로직, 에러 처리
- 세션 관리 및 User-Agent 랜덤화

#### HelpDocCrawler
- 도움말 문서에 특화된 크롤러
- 도움말 URL 패턴 자동 감지
- 사이트 전체 크롤링 지원
- 사이트맵 크롤링 지원

#### AdvancedSiteCrawler (Intercom 스타일)
- 링크 기반 탐색으로 사이트 전체 자동 크롤링
- URL Globs 패턴 매칭 지원
- CSS 선택자를 통한 요소 제어
- XML Sitemap 자동 감지 및 활용
- 하위 도메인 탐색 지원
- 사전 정의된 템플릿 (헬프 센터, 문서 사이트, 이커머스)

#### ContentExtractor
- HTML에서 깨끗한 텍스트 추출
- 네비게이션, 광고, 스크립트 제거
- 메인 콘텐츠 영역 자동 감지
- 메타데이터 추출 (제목, 헤딩, 링크 등)

## API 엔드포인트

### 크롤링 API
- `POST /api/crawling/projects/{id}/crawl` - URL 목록 크롤링
- `POST /api/crawling/projects/{id}/crawl/site` - 사이트 전체 크롤링
- `GET /api/crawling/projects/{id}/crawl/status` - 크롤링 상태 조회
- `GET /api/crawling/projects/{id}/crawl/stats` - 크롤링 통계
- `GET /api/crawling/projects/{id}/results` - 크롤링 결과 조회

### 고급 크롤링 API (Intercom 스타일)
- `POST /api/advanced-crawling/crawl-site` - 고급 사이트 크롤링
- `POST /api/advanced-crawling/crawl-help-center` - 헬프 센터 전용 크롤링
- `POST /api/advanced-crawling/crawl-documentation` - 문서 사이트 전용 크롤링
- `POST /api/advanced-crawling/crawl-custom` - 사용자 정의 설정 크롤링
- `GET /api/advanced-crawling/status/{project_id}` - 크롤링 상태 조회
- `POST /api/advanced-crawling/export/{project_id}` - 결과 내보내기
- `GET /api/advanced-crawling/config/templates` - 설정 템플릿 조회

### AI 분석 API
- `POST /api/ai/projects/{id}/analyze` - AI 기능 추출 분석
- `POST /api/ai/projects/{id}/analyze/batch` - 배치 AI 분석
- `GET /api/ai/projects/{id}/features` - 추출된 기능 목록
- `POST /api/ai/projects/{id}/analyze-keyword` - AI 키워드 분석
- `POST /api/ai/projects/{id}/compare-products` - 제품 비교 분석
- `GET /api/ai/status` - AI 서비스 상태 확인

자세한 API 문서는 [API_ENDPOINTS.md](backend/API_ENDPOINTS.md)를 참조하세요.

## 개발 가이드

### 크롤링 모듈 테스트
```bash
cd backend
python3 test_crawler.py
python3 test_advanced_crawler_simple.py  # 고급 크롤러 테스트
```

### 새로운 크롤러 추가
1. `BaseCrawler`를 상속받는 새 클래스 생성
2. `crawl()` 및 `crawl_multiple()` 메서드 구현
3. 필요한 경우 `ContentExtractor` 커스터마이징

### 데이터베이스 마이그레이션
```bash
flask db migrate -m "마이그레이션 설명"
flask db upgrade
```

## 라이선스

MIT License

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 로드맵

- [x] Vertex AI Gemini 통합
- [x] 자동 기능 식별
- [x] AI 기반 키워드 분석
- [x] 제품 비교 분석
- [ ] 경쟁 분석 리포트 자동 생성
- [ ] 다국어 지원
- [ ] 고급 필터링 및 검색
- [ ] 실시간 알림
- [ ] API 사용량 모니터링
