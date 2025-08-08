# Feature Detective API 엔드포인트

## 인증 관련 API (`/api/auth`)

### POST `/api/auth/register`

- **설명**: 사용자 등록
- **요청 본문**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **응답**: 201 Created
  ```json
  {
    "message": "회원가입이 완료되었습니다.",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
  ```

### POST `/api/auth/login`

- **설명**: 사용자 로그인
- **요청 본문**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **응답**: 200 OK
  ```json
  {
    "message": "로그인이 완료되었습니다.",
    "user": {
      "id": 1,
      "email": "user@example.com"
    }
  }
  ```

### POST `/api/auth/logout`

- **설명**: 사용자 로그아웃
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "message": "로그아웃이 완료되었습니다."
  }
  ```

### GET `/api/auth/me`

- **설명**: 현재 로그인한 사용자 정보 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "user": {
      "id": 1,
      "email": "user@example.com"
    }
  }
  ```

## 프로젝트 관리 API (`/api/projects`)

### GET `/api/projects`

- **설명**: 사용자의 프로젝트 목록 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "projects": [
      {
        "id": 1,
        "name": "프로젝트명",
        "description": "설명",
        "keyword_count": 5,
        "crawling_count": 10
      }
    ]
  }
  ```

### POST `/api/projects`

- **설명**: 새 프로젝트 생성
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "name": "새 프로젝트",
    "description": "프로젝트 설명"
  }
  ```
- **응답**: 201 Created
  ```json
  {
    "message": "프로젝트가 생성되었습니다.",
    "project": {
      "id": 1,
      "name": "새 프로젝트",
      "description": "프로젝트 설명"
    }
  }
  ```

### GET `/api/projects/{id}`

- **설명**: 특정 프로젝트 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "project": {
      "id": 1,
      "name": "프로젝트명",
      "description": "설명"
    }
  }
  ```

### PUT `/api/projects/{id}`

- **설명**: 프로젝트 수정
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "name": "수정된 프로젝트명",
    "description": "수정된 설명"
  }
  ```

### DELETE `/api/projects/{id}`

- **설명**: 프로젝트 삭제
- **인증**: 필요

## 키워드 관리 API (`/api/keywords`)

### GET `/api/keywords/projects/{project_id}/keywords`

- **설명**: 프로젝트의 키워드 목록 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "keywords": [
      {
        "id": 1,
        "keyword": "자동화",
        "category": "기능"
      }
    ]
  }
  ```

### POST `/api/keywords/projects/{project_id}/keywords`

- **설명**: 새 키워드 생성
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "keyword": "새 키워드",
    "category": "카테고리"
  }
  ```

### PUT `/api/keywords/keywords/{keyword_id}`

- **설명**: 키워드 수정
- **인증**: 필요

### DELETE `/api/keywords/keywords/{keyword_id}`

- **설명**: 키워드 삭제
- **인증**: 필요

### POST `/api/keywords/projects/{project_id}/keywords/upload`

- **설명**: CSV 파일로 키워드 업로드
- **인증**: 필요
- **요청**: multipart/form-data (file)

### GET `/api/keywords/projects/{project_id}/keywords/download`

- **설명**: 키워드 목록을 CSV로 다운로드
- **인증**: 필요

## 크롤링 관리 API (`/api/crawling`)

### POST `/api/crawling/projects/{project_id}/crawl`

- **설명**: 크롤링 시작
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "urls": ["https://example.com", "https://competitor.com"]
  }
  ```

### GET `/api/crawling/projects/{project_id}/crawl/status`

- **설명**: 크롤링 상태 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "status_summary": {
      "total": 10,
      "completed": 8,
      "processing": 1,
      "failed": 1
    },
    "results": [...]
  }
  ```

### GET `/api/crawling/projects/{project_id}/results`

- **설명**: 크롤링 결과 조회
- **인증**: 필요
- **쿼리 파라미터**: `page`, `per_page`

### GET `/api/crawling/results/{result_id}`

- **설명**: 특정 크롤링 결과 상세 조회
- **인증**: 필요

### DELETE `/api/crawling/results/{result_id}`

- **설명**: 크롤링 결과 삭제
- **인증**: 필요

## 리포트 생성 API (`/api/reports`)

### GET `/api/reports/projects/{project_id}/report/pdf`

- **설명**: PDF 리포트 생성
- **인증**: 필요
- **응답**: PDF 파일 다운로드

### GET `/api/reports/projects/{project_id}/report/csv`

- **설명**: CSV 리포트 생성
- **인증**: 필요
- **응답**: CSV 파일 다운로드

### GET `/api/reports/projects/{project_id}/report/summary`

- **설명**: 리포트 요약 정보 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "project": {...},
    "statistics": {
      "total_keywords": 10,
      "total_urls": 20,
      "support_stats": {
        "O": 15,
        "X": 3,
        "△": 2
      }
    },
    "keyword_stats": [...]
  }
  ```

### GET `/api/reports/projects/{project_id}/report/analysis`

- **설명**: 상세 분석 결과 조회
- **인증**: 필요
- **쿼리 파라미터**: `page`, `per_page`

## 헬스체크 API

### GET `/api/health`

- **설명**: API 서버 상태 확인
- **응답**: 200 OK
  ```json
  {
    "status": "healthy",
    "message": "Feature Detective API is running"
  }
  ```

## 에러 응답 형식

모든 API는 에러 발생 시 다음과 같은 형식으로 응답합니다:

```json
{
  "error": "에러 메시지"
}
```

### HTTP 상태 코드

- `200`: 성공
- `201`: 생성됨
- `400`: 잘못된 요청
- `401`: 인증 필요
- `404`: 리소스를 찾을 수 없음
- `409`: 충돌 (중복 등)
- `500`: 서버 내부 오류
