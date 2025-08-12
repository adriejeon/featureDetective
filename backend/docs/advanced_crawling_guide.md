# 고급 크롤링 가이드

## 개요

Feature Detective의 고급 크롤링 기능은 Intercom과 같은 전문적인 웹 크롤링 서비스와 유사한 기능을 제공합니다. 이 기능을 통해 웹사이트의 모든 하위 페이지를 자동으로 탐색하고 크롤링할 수 있습니다.

## 주요 기능

### 1. 링크 기반 탐색 방식
- 입력된 URL을 시작점으로 하여 하이퍼링크를 따라 자동으로 페이지를 탐색
- BFS(너비 우선 탐색) 알고리즘을 사용하여 효율적인 크롤링
- 깊이 제한을 통한 탐색 범위 제어

### 2. URL Globs 지원
- 와일드카드를 사용한 URL 패턴 매칭
- 포함할 URL 패턴과 제외할 URL 패턴을 설정 가능
- 예: `*/help/*`, `*/docs/*`, `*.pdf` 등

### 3. CSS 선택자를 통한 제어
- 불필요한 HTML 요소 제외 (nav, footer, ads 등)
- 숨겨진 콘텐츠 클릭 및 대기 설정
- 정확한 콘텐츠 추출을 위한 요소 필터링

### 4. XML Sitemap 활용
- robots.txt에서 sitemap 정보 자동 감지
- sitemap.xml을 통한 빠른 페이지 발견
- sitemap index 처리 지원

### 5. 하위 도메인 탐색
- 같은 도메인의 하위 도메인 자동 탐색
- 설정을 통한 하위 도메인 탐색 제어

## API 사용법

### 기본 고급 크롤링

```bash
POST /api/advanced-crawling/crawl-site
```

**Request Body:**
```json
{
  "project_id": 1,
  "base_url": "https://example.com",
  "config": {
    "max_pages": 50,
    "max_depth": 3,
    "include_patterns": ["*/help/*", "*/docs/*"],
    "exclude_patterns": ["*.pdf", "*.zip"],
    "css_exclude_selectors": ["nav", "footer"]
  }
}
```

### 헬프 센터 전용 크롤링

```bash
POST /api/advanced-crawling/crawl-help-center
```

**Request Body:**
```json
{
  "project_id": 1,
  "base_url": "https://example.com/help"
}
```

### 문서 사이트 전용 크롤링

```bash
POST /api/advanced-crawling/crawl-documentation
```

**Request Body:**
```json
{
  "project_id": 1,
  "base_url": "https://example.com/docs"
}
```

### 사용자 정의 설정으로 크롤링

```bash
POST /api/advanced-crawling/crawl-custom
```

**Request Body:**
```json
{
  "project_id": 1,
  "base_url": "https://example.com",
  "include_patterns": ["*/help/*", "*/docs/*"],
  "exclude_patterns": ["*.pdf", "*.zip"],
  "css_exclude_selectors": ["nav", "footer"],
  "max_pages": 50,
  "max_depth": 3
}
```

## 설정 옵션

### CrawlConfig 클래스

```python
@dataclass
class CrawlConfig:
    max_pages: int = 100              # 최대 크롤링할 페이지 수
    max_depth: int = 3                # 최대 탐색 깊이
    rate_limit: float = 1.0           # 요청 간 대기 시간 (초)
    timeout: int = 30                 # 요청 타임아웃 (초)
    follow_subdomains: bool = True    # 하위 도메인 탐색 여부
    include_patterns: List[str] = None    # 포함할 URL 패턴
    exclude_patterns: List[str] = None    # 제외할 URL 패턴
    css_exclude_selectors: List[str] = None  # 제외할 CSS 선택자
    css_click_selectors: List[str] = None    # 클릭할 CSS 선택자
    css_wait_selectors: List[str] = None     # 대기할 CSS 선택자
    use_sitemap: bool = True          # Sitemap 사용 여부
    respect_robots_txt: bool = True   # robots.txt 준수 여부
    user_agent: str = None            # 사용자 정의 User-Agent
```

### 기본 제외 패턴

```python
exclude_patterns = [
    '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx',
    '*.zip', '*.rar', '*.tar', '*.gz',
    '*.jpg', '*.jpeg', '*.png', '*.gif', '*.svg',
    '*.mp4', '*.avi', '*.mov', '*.wmv',
    'mailto:', 'tel:', 'javascript:',
    '/admin/', '/login/', '/logout/', '/register/',
    '/api/', '/ajax/', '/json/', '/xml/',
    '?utm_', '?fbclid', '?gclid'
]
```

### 기본 CSS 제외 선택자

```python
css_exclude_selectors = [
    'nav', 'footer', 'header', 'aside', 'sidebar',
    '.advertisement', '.ads', '.banner', '.popup',
    '.cookie-notice', '.newsletter', '.social-share',
    'script', 'style', 'noscript'
]
```

## 사전 정의된 템플릿

### 헬프 센터 템플릿

```python
help_center_config = {
    'max_pages': 100,
    'max_depth': 4,
    'include_patterns': [
        '*/help/*', '*/support/*', '*/docs/*', '*/guide/*',
        '*/manual/*', '*/tutorial/*', '*/faq/*', '*/knowledge/*'
    ],
    'exclude_patterns': [
        '*.pdf', '*.doc', '*.docx', '*.zip', '*.rar',
        'mailto:', 'tel:', 'javascript:',
        '/admin/', '/login/', '/logout/', '/register/',
        '?utm_', '?fbclid', '?gclid'
    ]
}
```

### 문서 사이트 템플릿

```python
documentation_config = {
    'max_pages': 200,
    'max_depth': 5,
    'include_patterns': [
        '*/docs/*', '*/documentation/*', '*/api/*', '*/reference/*',
        '*/guide/*', '*/tutorial/*', '*/examples/*', '*/getting-started/*'
    ],
    'exclude_patterns': [
        '*.pdf', '*.zip', '*.tar.gz',
        'mailto:', 'tel:', 'javascript:',
        '/admin/', '/login/', '/logout/',
        '?utm_', '?fbclid', '?gclid'
    ]
}
```

### 이커머스 사이트 템플릿

```python
ecommerce_config = {
    'max_pages': 150,
    'max_depth': 4,
    'include_patterns': [
        '*/product/*', '*/category/*', '*/shop/*',
        '*/help/*', '*/support/*', '*/faq/*'
    ],
    'exclude_patterns': [
        '*.pdf', '*.zip', '*.rar',
        'mailto:', 'tel:', 'javascript:',
        '/cart/', '/checkout/', '/login/', '/register/',
        '?utm_', '?fbclid', '?gclid'
    ]
}
```

## 사용 예시

### Python에서 직접 사용

```python
from crawlers.advanced_site_crawler import AdvancedSiteCrawler, CrawlConfig

# 기본 설정으로 크롤러 생성
config = CrawlConfig(
    max_pages=50,
    max_depth=3,
    include_patterns=['*/help/*', '*/docs/*'],
    exclude_patterns=['*.pdf', 'mailto:']
)

crawler = AdvancedSiteCrawler(config)

# 크롤링 실행
results = crawler.crawl('https://example.com')

# 결과 출력
for result in results:
    print(f"제목: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"콘텐츠 길이: {result['content_length']}자")
    print("---")

# 통계 확인
stats = crawler.get_crawl_stats()
print(f"총 페이지: {stats['total_pages']}")
print(f"성공: {stats['successful_pages']}")
print(f"실패: {stats['failed_pages']}")

# 결과 내보내기
crawler.export_results('results.json', 'json')
crawler.export_results('results.csv', 'csv')

crawler.close()
```

### 서비스를 통한 사용

```python
from services.advanced_crawling_service import AdvancedCrawlingService

service = AdvancedCrawlingService()

# 헬프 센터 크롤링
results = service.crawl_help_center('https://example.com/help', project_id=1)

# 문서 사이트 크롤링
results = service.crawl_documentation('https://example.com/docs', project_id=1)

# 사용자 정의 설정으로 크롤링
results = service.crawl_with_custom_settings(
    base_url='https://example.com',
    project_id=1,
    include_patterns=['*/help/*', '*/docs/*'],
    exclude_patterns=['*.pdf', '*.zip'],
    max_pages=50,
    max_depth=3
)
```

## 모니터링 및 관리

### 크롤링 상태 조회

```bash
GET /api/advanced-crawling/status/{project_id}
```

### 결과 내보내기

```bash
POST /api/advanced-crawling/export/{project_id}
```

**Request Body:**
```json
{
  "format": "json",  // "json" 또는 "csv"
  "filepath": "/path/to/export/file.json"
}
```

### 설정 템플릿 조회

```bash
GET /api/advanced-crawling/config/templates
```

## 성능 최적화 팁

1. **적절한 rate_limit 설정**: 서버에 부하를 주지 않도록 1-2초 간격 권장
2. **max_pages 제한**: 필요한 페이지만 크롤링하도록 설정
3. **max_depth 제한**: 깊이가 깊을수록 시간이 오래 걸림
4. **패턴 최적화**: 정확한 include/exclude 패턴으로 불필요한 페이지 제외
5. **CSS 선택자 활용**: 정확한 콘텐츠 추출을 위한 요소 필터링

## 주의사항

1. **robots.txt 준수**: 웹사이트의 robots.txt 규칙을 준수하세요
2. **적절한 대기 시간**: 서버에 과부하를 주지 않도록 rate_limit을 설정하세요
3. **저작권 준수**: 크롤링한 콘텐츠의 저작권을 준수하세요
4. **서버 리소스**: 대용량 크롤링 시 서버 리소스를 고려하세요
5. **에러 처리**: 네트워크 오류나 서버 오류에 대한 적절한 처리

## 문제 해결

### 일반적인 문제들

1. **크롤링이 너무 느림**
   - rate_limit을 줄여보세요
   - max_pages나 max_depth를 줄여보세요

2. **불필요한 페이지가 크롤링됨**
   - exclude_patterns를 더 구체적으로 설정하세요
   - include_patterns를 사용하여 원하는 페이지만 포함하세요

3. **콘텐츠가 제대로 추출되지 않음**
   - css_exclude_selectors를 조정해보세요
   - 페이지 구조를 확인하고 적절한 선택자를 사용하세요

4. **메모리 사용량이 높음**
   - max_pages를 줄여보세요
   - 크롤링 결과를 주기적으로 저장하세요
