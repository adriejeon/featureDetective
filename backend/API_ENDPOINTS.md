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

- **설명**: URL 목록 크롤링 시작
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "urls": ["https://example.com/help", "https://competitor.com/docs"]
  }
  ```
- **응답**: 202 Accepted
  ```json
  {
    "message": "크롤링이 시작되었습니다.",
    "task_id": "task-uuid"
  }
  ```

### POST `/api/crawling/projects/{project_id}/crawl/site`

- **설명**: 사이트 전체 크롤링 시작
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "base_url": "https://example.com/help",
    "follow_links": true
  }
  ```
- **응답**: 202 Accepted
  ```json
  {
    "message": "사이트 크롤링이 시작되었습니다.",
    "task_id": "task-uuid",
    "base_url": "https://example.com/help",
    "follow_links": true
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
      "failed": 1,
      "pending": 0
    },
    "total_results": 10,
    "recent_results": [
      {
        "id": 1,
        "url": "https://example.com/help",
        "status": "completed",
        "crawled_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
  ```

### GET `/api/crawling/projects/{project_id}/crawl/stats`

- **설명**: 크롤링 통계 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "crawl_stats": {
      "crawled_urls": 15,
      "max_depth": 2,
      "max_pages": 50,
      "rate_limiter_stats": {
        "requests_per_second": 1.0,
        "burst_size": 5,
        "recent_requests": 1,
        "queue_size": 1
      }
    }
  }
  ```

### GET `/api/crawling/projects/{project_id}/results`

- **설명**: 크롤링 결과 조회
- **인증**: 필요
- **쿼리 파라미터**: `page`, `per_page`, `status` (필터링)
- **응답**: 200 OK
  ```json
  {
    "results": [
      {
        "id": 1,
        "url": "https://example.com/help",
        "content": "크롤링된 콘텐츠...",
        "status": "completed",
        "content_length": 1500,
        "extraction_method": "main_content",
        "metadata": {
          "title": "도움말 페이지",
          "headings": [...],
          "links": [...]
        },
        "crawled_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "pages": 3
    }
  }
  ```

### GET `/api/crawling/results/{result_id}`

- **설명**: 특정 크롤링 결과 상세 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "result": {
      "id": 1,
      "url": "https://example.com/help",
      "content": "전체 크롤링된 콘텐츠",
      "status": "completed",
      "content_length": 1500,
      "extraction_method": "main_content",
      "metadata": {...},
      "crawled_at": "2024-01-15T10:30:00Z"
    }
  }
  ```

### DELETE `/api/crawling/results/{result_id}`

- **설명**: 크롤링 결과 삭제
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "message": "크롤링 결과가 삭제되었습니다."
  }
  ```

### DELETE `/api/crawling/projects/{project_id}/results/bulk-delete`

- **설명**: 프로젝트의 모든 크롤링 결과 삭제
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "message": "15개의 크롤링 결과가 삭제되었습니다.",
    "deleted_count": 15
  }
  ```

## AI 분석 API (`/api/ai`)

### POST `/api/ai/projects/{project_id}/analyze`

- **설명**: 크롤링된 콘텐츠에 AI 분석 수행
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "crawling_result_id": 123
  }
  ```
- **응답**: 202 Accepted
  ```json
  {
    "message": "AI 분석이 시작되었습니다.",
    "task_id": "task-uuid",
    "crawling_result_id": 123
  }
  ```

### POST `/api/ai/projects/{project_id}/analyze/batch`

- **설명**: 여러 크롤링 결과에 배치 AI 분석 수행
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "crawling_result_ids": [123, 124, 125]
  }
  ```
- **응답**: 202 Accepted
  ```json
  {
    "message": "3개 결과에 대한 배치 AI 분석이 시작되었습니다.",
    "task_id": "task-uuid",
    "crawling_result_ids": [123, 124, 125]
  }
  ```

### GET `/api/ai/projects/{project_id}/features`

- **설명**: 추출된 기능 목록 조회
- **인증**: 필요
- **쿼리 파라미터**: `page`, `per_page`, `category` (필터링)
- **응답**: 200 OK
  ```json
  {
    "features": [
      {
        "id": 1,
        "feature_name": "API 통합",
        "category": "통합",
        "description": "외부 API와의 연동 기능",
        "confidence_score": 0.95,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "pages": 3
    }
  }
  ```

### GET `/api/ai/projects/{project_id}/features/summary`

- **설명**: 추출된 기능 요약 정보 조회
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "total_features": 25,
    "average_confidence": 0.87,
    "category_stats": [
      {
        "category": "통합",
        "count": 8,
        "average_confidence": 0.92
      },
      {
        "category": "보안",
        "count": 5,
        "average_confidence": 0.85
      }
    ]
  }
  ```

### POST `/api/ai/projects/{project_id}/analyze-keyword`

- **설명**: AI를 사용한 키워드 분석
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "keyword": "실시간 알림",
    "content": "분석할 도움말 텍스트 내용..."
  }
  ```
- **응답**: 200 OK
  ```json
  {
    "keyword": "실시간 알림",
    "analysis_result": {
      "support_status": "O",
      "confidence_score": 0.92,
      "matched_text": "실시간 알림 기능을 통해...",
      "analysis_reason": "명시적으로 실시간 알림 기능이 언급됨",
      "related_features": ["푸시 알림", "이메일 알림"],
      "limitations": []
    }
  }
  ```

### POST `/api/ai/projects/{project_id}/compare-products`

- **설명**: AI를 사용한 제품 비교 분석
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "product1": {
      "name": "제품A",
      "features": [
        {"name": "API 통합", "category": "통합"},
        {"name": "실시간 알림", "category": "기능"}
      ]
    },
    "product2": {
      "name": "제품B",
      "features": [
        {"name": "API 연동", "category": "통합"},
        {"name": "이메일 알림", "category": "기능"}
      ]
    }
  }
  ```
- **응답**: 200 OK
  ```json
  {
    "comparison_result": {
      "comparison_summary": {
        "total_features_product1": 2,
        "total_features_product2": 2,
        "common_features": 1,
        "unique_features_product1": 1,
        "unique_features_product2": 1
      },
      "feature_comparison": [
        {
          "feature_name": "API 통합",
          "product1_support": true,
          "product2_support": true,
          "comparison_type": "common",
          "significance": "high"
        }
      ],
      "competitive_analysis": {
        "product1_advantages": ["실시간 알림"],
        "product2_advantages": ["이메일 알림"],
        "market_positioning": "두 제품 모두 API 통합에 강점",
        "recommendations": ["실시간 알림 기능 강화"]
      }
    }
  }
  ```

### GET `/api/ai/projects/{project_id}/comparisons`

- **설명**: 제품 비교 분석 결과 목록 조회
- **인증**: 필요
- **쿼리 파라미터**: `page`, `per_page`
- **응답**: 200 OK
  ```json
  {
    "comparisons": [
      {
        "id": 1,
        "product1_name": "제품A",
        "product2_name": "제품B",
        "comparison_data": {...},
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 5,
      "pages": 1
    }
  }
  ```

### GET `/api/ai/status`

- **설명**: AI 서비스 상태 확인
- **응답**: 200 OK
  ```json
  {
    "ai_services": {
      "vertex_ai": "available",
      "project_id": "groobee-ai",
      "model": "gemini-2.5-flash-lite"
    }
  }
  ```

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
