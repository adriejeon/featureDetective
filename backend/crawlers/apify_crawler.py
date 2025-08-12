"""
Apify Crawlee 기반 고급 크롤러
Intercom과 같은 고급 크롤링 기능을 제공하는 크롤러
- Playwright 기반 브라우저 자동화
- JavaScript 실행 및 동적 콘텐츠 처리
- 고급 링크 탐색 및 상호작용
- 스마트 필터링 및 세션 관리
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse
import json
import re
from datetime import timedelta

from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee import Request

logger = logging.getLogger(__name__)


@dataclass
class ApifyCrawlConfig:
    """Apify 크롤링 설정"""
    max_pages: int = 100
    max_depth: int = 3
    rate_limit: float = 1.0
    timeout: int = 30000
    headless: bool = True
    follow_subdomains: bool = True
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    css_exclude_selectors: List[str] = field(default_factory=list)
    css_click_selectors: List[str] = field(default_factory=list)
    css_wait_selectors: List[str] = field(default_factory=list)
    use_sitemap: bool = True
    respect_robots_txt: bool = True
    wait_for_network_idle: bool = True
    max_concurrent_pages: int = 3
    
    def __post_init__(self):
        if not self.exclude_patterns:
            self.exclude_patterns = [
                '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx',
                '*.zip', '*.rar', '*.tar', '*.gz',
                '*.jpg', '*.jpeg', '*.png', '*.gif', '*.svg',
                '*.mp4', '*.avi', '*.mov', '*.wmv',
                'mailto:', 'tel:', 'javascript:',
                '/admin/', '/login/', '/logout/', '/register/',
                '/api/', '/ajax/', '/json/', '/xml/',
                '?utm_', '?fbclid', '?gclid'
            ]
        if not self.css_exclude_selectors:
            self.css_exclude_selectors = [
                'nav', 'footer', 'header', 'aside', 'sidebar',
                '.advertisement', '.ads', '.banner', '.popup',
                '.cookie-notice', '.newsletter', '.social-share',
                'script', 'style', 'noscript'
            ]


class ApifyAdvancedCrawler:
    """Apify Crawlee 기반 고급 크롤러"""
    
    def __init__(self, config: ApifyCrawlConfig = None):
        """
        고급 크롤러 초기화
        
        Args:
            config: 크롤링 설정
        """
        self.config = config or ApifyCrawlConfig()
        self.visited_urls: Set[str] = set()
        self.crawl_results: List[Dict] = []
        
        # 통계
        self.stats = {
            'total_pages': 0,
            'successful_pages': 0,
            'failed_pages': 0,
            'excluded_pages': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def crawl_site(self, base_url: str, project_id: int) -> List[Dict]:
        """
        사이트 크롤링 실행
        
        Args:
            base_url: 크롤링할 기본 URL
            project_id: 프로젝트 ID
            
        Returns:
            크롤링 결과 리스트
        """
        logger.info(f"Apify 크롤러로 사이트 크롤링 시작: {base_url}")
        
        # 크롤러 생성
        crawler = PlaywrightCrawler(
            max_requests_per_crawl=self.config.max_pages,
            headless=self.config.headless,
            browser_launch_options={
                'args': ['--disable-gpu', '--no-sandbox'],
            },
            request_handler_timeout=timedelta(seconds=self.config.timeout // 1000),
        )
        
        # 요청 핸들러 정의
        @crawler.router.default_handler
        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            url = context.request.url
            logger.info(f'크롤링 중: {url}')
            
            try:
                # 페이지 로딩 대기
                await context.page.wait_for_load_state('networkidle')
                
                # CSS 선택자로 클릭 (필요한 경우)
                for selector in self.config.css_click_selectors:
                    try:
                        await context.page.click(selector)
                        await context.page.wait_for_timeout(1000)
                    except Exception as e:
                        logger.debug(f"클릭 실패 ({selector}): {e}")
                
                # CSS 선택자로 대기 (필요한 경우)
                for selector in self.config.css_wait_selectors:
                    try:
                        await context.page.wait_for_selector(selector, timeout=5000)
                    except Exception as e:
                        logger.debug(f"대기 실패 ({selector}): {e}")
                
                # 콘텐츠 추출
                data = await self._extract_content(context)
                
                # 결과 저장
                self.crawl_results.append({
                    'project_id': project_id,
                    'url': url,
                    'content': data.get('content', ''),
                    'title': data.get('title', ''),
                    'headings': data.get('headings', {}),
                    'links': data.get('links', []),
                    'status': 'completed',
                    'error_message': None,
                    'crawled_at': None,
                    'content_length': len(data.get('content', '')),
                    'extraction_method': 'apify_playwright_crawler',
                    'crawling_metadata': {
                        'title': data.get('title', ''),
                        'headings': data.get('headings', {}),
                        'links_count': len(data.get('links', [])),
                        'content_length': len(data.get('content', ''))
                    }
                })
                
                self.stats['successful_pages'] += 1
                
                # 추가 링크 탐색
                await self._enqueue_links(context, base_url)
                
            except Exception as e:
                logger.error(f"페이지 크롤링 실패 ({url}): {e}")
                self.crawl_results.append({
                    'project_id': project_id,
                    'url': url,
                    'content': '',
                    'title': '',
                    'headings': {},
                    'links': [],
                    'status': 'failed',
                    'error_message': str(e),
                    'crawled_at': None,
                    'content_length': 0,
                    'extraction_method': 'apify_playwright_crawler',
                    'crawling_metadata': {}
                })
                self.stats['failed_pages'] += 1
        
        # 크롤링 실행
        await crawler.run([base_url])
        
        logger.info(f"크롤링 완료: {len(self.crawl_results)}개 페이지")
        return self.crawl_results
    
    async def _extract_content(self, context: PlaywrightCrawlingContext) -> Dict[str, Any]:
        """페이지에서 콘텐츠 추출"""
        try:
            # 제목 추출
            title = await context.page.title()
            
            # 제외할 요소들 제거
            for selector in self.config.css_exclude_selectors:
                try:
                    await context.page.evaluate(f'''
                        document.querySelectorAll('{selector}').forEach(el => el.remove());
                    ''')
                except Exception as e:
                    logger.debug(f"요소 제거 실패 ({selector}): {e}")
            
            # 헤딩 추출
            headings = {}
            for level in range(1, 7):
                h_elements = await context.page.locator(f'h{level}').all()
                headings[f'h{level}'] = [
                    await h.text_content() for h in h_elements
                ]
            
            # 텍스트 콘텐츠 추출
            content = await context.page.evaluate('''
                () => {
                    const body = document.body;
                    if (!body) return '';
                    
                    // 텍스트만 추출
                    const text = body.innerText || body.textContent || '';
                    
                    // 줄바꿈 정리
                    return text.replace(/\\s+/g, ' ').trim();
                }
            ''')
            
            # 링크 추출
            links = await context.page.evaluate('''
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(link => ({
                        url: link.href,
                        text: link.textContent?.trim() || '',
                        title: link.title || ''
                    }));
                }
            ''')
            
            return {
                'title': title,
                'content': content,
                'headings': headings,
                'links': links
            }
            
        except Exception as e:
            logger.error(f"콘텐츠 추출 실패: {e}")
            return {
                'title': '',
                'content': '',
                'headings': {},
                'links': []
            }
    
    async def _enqueue_links(self, context: PlaywrightCrawlingContext, base_url: str):
        """추가 링크를 큐에 추가"""
        try:
            # 현재 도메인의 링크만 필터링
            base_domain = urlparse(base_url).netloc
            
            # 링크 추출 및 필터링
            links = await context.page.evaluate(f'''
                () => {{
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const baseDomain = '{base_domain}';
                    
                    return links
                        .map(link => link.href)
                        .filter(href => {{
                            try {{
                                const url = new URL(href);
                                return url.hostname === baseDomain || url.hostname.endsWith('.' + baseDomain);
                            }} catch {{
                                return false;
                            }}
                        }})
                        .filter(href => {{
                            // 제외 패턴 체크
                            const excludePatterns = {json.dumps(self.config.exclude_patterns)};
                            return !excludePatterns.some(pattern => {{
                                if (pattern.includes('*')) {{
                                    const regex = new RegExp(pattern.replace(/\\*/g, '.*'));
                                    return regex.test(href);
                                }}
                                return href.includes(pattern);
                            }});
                        }})
                        .slice(0, 50); // 최대 50개 링크만
                }}
            ''')
            
            # 새 링크들을 큐에 추가
            for link in links:
                if link not in self.visited_urls:
                    await context.enqueue_links([Request(link)])
                    self.visited_urls.add(link)
            
        except Exception as e:
            logger.error(f"링크 큐 추가 실패: {e}")
    
    def _match_url_pattern(self, url: str, patterns: List[str]) -> bool:
        """URL 패턴 매칭"""
        for pattern in patterns:
            if pattern.endswith('*'):
                if url.startswith(pattern[:-1]):
                    return True
            elif pattern in url:
                return True
        return False


# 비동기 실행을 위한 래퍼 함수
def run_apify_crawler(base_url: str, project_id: int, config: ApifyCrawlConfig = None) -> List[Dict]:
    """
    Apify 크롤러 실행 (동기 래퍼)
    
    Args:
        base_url: 크롤링할 기본 URL
        project_id: 프로젝트 ID
        config: 크롤링 설정
        
    Returns:
        크롤링 결과 리스트
    """
    crawler = ApifyAdvancedCrawler(config)
    return asyncio.run(crawler.crawl_site(base_url, project_id))
