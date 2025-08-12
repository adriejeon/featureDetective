"""
고급 사이트 크롤러
Intercom과 같은 고급 크롤링 기능을 제공하는 크롤러
- 링크 기반 탐색 방식
- URL globs 지원
- CSS 선택자를 통한 제외/클릭/대기 설정
- XML Sitemap 활용
- 하위 도메인 탐색
"""

import requests
import time
import logging
import re
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class CrawlConfig:
    """크롤링 설정"""
    max_pages: int = 100
    max_depth: int = 3
    rate_limit: float = 1.0
    timeout: int = 30
    follow_subdomains: bool = True
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None
    css_exclude_selectors: List[str] = None
    css_click_selectors: List[str] = None
    css_wait_selectors: List[str] = None
    use_sitemap: bool = True
    respect_robots_txt: bool = True
    user_agent: str = None
    
    def __post_init__(self):
        if self.include_patterns is None:
            self.include_patterns = []
        if self.exclude_patterns is None:
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
        if self.css_exclude_selectors is None:
            self.css_exclude_selectors = [
                'nav', 'footer', 'header', 'aside', 'sidebar',
                '.advertisement', '.ads', '.banner', '.popup',
                '.cookie-notice', '.newsletter', '.social-share',
                'script', 'style', 'noscript'
            ]
        if self.css_click_selectors is None:
            self.css_click_selectors = []
        if self.css_wait_selectors is None:
            self.css_wait_selectors = []
        if self.user_agent is None:
            self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


class AdvancedSiteCrawler:
    """고급 사이트 크롤러"""
    
    def __init__(self, config: CrawlConfig = None):
        """
        고급 크롤러 초기화
        
        Args:
            config: 크롤링 설정
        """
        self.config = config or CrawlConfig()
        self.session = self._create_session()
        self.visited_urls: Set[str] = set()
        self.url_queue: List[Dict] = []
        self.crawl_results: List[Dict] = []
        self.last_request_time = 0
        
        # 통계
        self.stats = {
            'total_pages': 0,
            'successful_pages': 0,
            'failed_pages': 0,
            'excluded_pages': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _create_session(self) -> requests.Session:
        """강화된 세션 생성"""
        session = requests.Session()
        
        # 재시도 전략
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 헤더 설정
        session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _rate_limit(self):
        """요청 간 대기 시간 적용"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.config.rate_limit:
            sleep_time = self.config.rate_limit - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _matches_pattern(self, url: str, patterns: List[str]) -> bool:
        """URL이 패턴과 일치하는지 확인"""
        for pattern in patterns:
            if pattern.startswith('*'):
                # 와일드카드 패턴
                if pattern.endswith('*'):
                    if pattern[1:-1] in url:
                        return True
                elif pattern.endswith('/'):
                    if url.endswith(pattern[1:]):
                        return True
                else:
                    if url.endswith(pattern[1:]):
                        return True
            elif pattern in url:
                return True
        return False
    
    def _should_crawl_url(self, url: str, base_domain: str) -> bool:
        """URL을 크롤링해야 하는지 결정"""
        try:
            parsed = urlparse(url)
            
            # 이미 방문한 URL
            if url in self.visited_urls:
                return False
            
            # 제외 패턴 확인
            if self._matches_pattern(url, self.config.exclude_patterns):
                logger.debug(f"제외 패턴에 의해 스킵: {url}")
                return False
            
            # 포함 패턴이 있으면 포함 패턴 확인
            if self.config.include_patterns and not self._matches_pattern(url, self.config.include_patterns):
                logger.debug(f"포함 패턴에 없어서 스킵: {url}")
                return False
            
            # 같은 도메인 확인
            if not self._is_same_domain(parsed.netloc, base_domain):
                return False
            
            # 하위 도메인 확인
            if not self.config.follow_subdomains and parsed.netloc != base_domain:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL 검증 중 오류 ({url}): {e}")
            return False
    
    def _is_same_domain(self, domain1: str, domain2: str) -> bool:
        """같은 도메인인지 확인"""
        if domain1 == domain2:
            return True
        
        # 하위 도메인 확인
        if self.config.follow_subdomains:
            if domain1.endswith('.' + domain2) or domain2.endswith('.' + domain1):
                return True
        
        return False
    
    def _get_sitemap_urls(self, base_url: str) -> List[str]:
        """XML Sitemap에서 URL 추출"""
        sitemap_urls = []
        
        try:
            # robots.txt에서 sitemap 찾기
            robots_url = urljoin(base_url, '/robots.txt')
            if self.config.respect_robots_txt:
                try:
                    response = self.session.get(robots_url, timeout=self.config.timeout)
                    if response.status_code == 200:
                        for line in response.text.split('\n'):
                            if line.lower().startswith('sitemap:'):
                                sitemap_url = line.split(':', 1)[1].strip()
                                sitemap_urls.extend(self._parse_sitemap(sitemap_url))
                except Exception as e:
                    logger.warning(f"robots.txt 읽기 실패: {e}")
            
            # 일반적인 sitemap 위치들 시도
            common_sitemaps = [
                urljoin(base_url, '/sitemap.xml'),
                urljoin(base_url, '/sitemap_index.xml'),
                urljoin(base_url, '/sitemap/sitemap.xml'),
            ]
            
            for sitemap_url in common_sitemaps:
                try:
                    sitemap_urls.extend(self._parse_sitemap(sitemap_url))
                except Exception as e:
                    logger.debug(f"sitemap 읽기 실패 ({sitemap_url}): {e}")
            
            logger.info(f"sitemap에서 {len(sitemap_urls)}개 URL 발견")
            return sitemap_urls
            
        except Exception as e:
            logger.error(f"sitemap 처리 중 오류: {e}")
            return []
    
    def _parse_sitemap(self, sitemap_url: str) -> List[str]:
        """XML Sitemap 파싱"""
        urls = []
        
        try:
            response = self.session.get(sitemap_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # sitemap index 처리
            if 'sitemapindex' in root.tag:
                for sitemap in root.findall('.//{*}sitemap/{*}loc'):
                    urls.extend(self._parse_sitemap(sitemap.text))
            else:
                # 일반 sitemap 처리
                for url in root.findall('.//{*}url/{*}loc'):
                    urls.append(url.text)
            
            return urls
            
        except Exception as e:
            logger.error(f"sitemap 파싱 실패 ({sitemap_url}): {e}")
            return []
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """페이지에서 링크 추출"""
        links = []
        
        try:
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href:
                    # 상대 URL을 절대 URL로 변환
                    absolute_url = urljoin(base_url, href)
                    links.append(absolute_url)
            
            return links
            
        except Exception as e:
            logger.error(f"링크 추출 중 오류: {e}")
            return []
    
    def _clean_content(self, soup: BeautifulSoup) -> str:
        """콘텐츠 정리"""
        try:
            # 제외할 요소들 제거
            for selector in self.config.css_exclude_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            # 텍스트 추출
            text = soup.get_text()
            
            # 텍스트 정리
            lines = []
            for line in text.split('\n'):
                line = line.strip()
                if line and len(line) > 2:
                    lines.append(line)
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"콘텐츠 정리 중 오류: {e}")
            return ""
    
    def _fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """페이지 가져오기"""
        try:
            self._rate_limit()
            
            logger.info(f"페이지 요청: {url}")
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            # 인코딩 처리
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'content': self._clean_content(soup),
                'soup': soup,
                'status_code': response.status_code,
                'content_length': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"페이지 가져오기 실패 ({url}): {e}")
            return None
    
    def crawl(self, base_url: str) -> List[Dict[str, Any]]:
        """
        사이트 크롤링 실행
        
        Args:
            base_url: 크롤링할 기본 URL
            
        Returns:
            크롤링 결과 리스트
        """
        logger.info(f"고급 사이트 크롤링 시작: {base_url}")
        
        self.stats['start_time'] = time.time()
        self.visited_urls.clear()
        self.url_queue.clear()
        self.crawl_results.clear()
        
        try:
            parsed_base = urlparse(base_url)
            base_domain = parsed_base.netloc
            
            # 초기 URL을 큐에 추가
            self.url_queue.append({
                'url': base_url,
                'depth': 0,
                'source': 'initial'
            })
            
            # Sitemap에서 URL 추가
            if self.config.use_sitemap:
                sitemap_urls = self._get_sitemap_urls(base_url)
                for url in sitemap_urls:
                    if self._should_crawl_url(url, base_domain):
                        self.url_queue.append({
                            'url': url,
                            'depth': 0,
                            'source': 'sitemap'
                        })
            
            # BFS로 크롤링
            while self.url_queue and len(self.crawl_results) < self.config.max_pages:
                current = self.url_queue.pop(0)
                url = current['url']
                depth = current['depth']
                
                if url in self.visited_urls:
                    continue
                
                self.visited_urls.add(url)
                self.stats['total_pages'] += 1
                
                # 페이지 가져오기
                page_data = self._fetch_page(url)
                if page_data:
                    self.stats['successful_pages'] += 1
                    
                    # 결과 저장
                    result = {
                        'title': page_data['title'],
                        'url': url,
                        'content': page_data['content'],
                        'depth': depth,
                        'source': current['source'],
                        'content_length': page_data['content_length'],
                        'status_code': page_data['status_code']
                    }
                    self.crawl_results.append(result)
                    
                    # 다음 레벨 링크 추가
                    if depth < self.config.max_depth:
                        links = self._extract_links(page_data['soup'], url)
                        for link in links:
                            if self._should_crawl_url(link, base_domain):
                                self.url_queue.append({
                                    'url': link,
                                    'depth': depth + 1,
                                    'source': 'link'
                                })
                else:
                    self.stats['failed_pages'] += 1
            
            self.stats['end_time'] = time.time()
            
            logger.info(f"크롤링 완료: {len(self.crawl_results)}개 페이지")
            logger.info(f"통계: {self.stats}")
            
            return self.crawl_results
            
        except Exception as e:
            logger.error(f"크롤링 중 오류: {e}")
            return []
    
    def get_crawl_stats(self) -> Dict[str, Any]:
        """크롤링 통계 반환"""
        stats = self.stats.copy()
        if stats['start_time'] and stats['end_time']:
            stats['duration'] = stats['end_time'] - stats['start_time']
        return stats
    
    def export_results(self, filepath: str, format: str = 'json'):
        """크롤링 결과 내보내기"""
        try:
            if format.lower() == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        'crawl_results': self.crawl_results,
                        'stats': self.get_crawl_stats(),
                        'config': self.config.__dict__
                    }, f, ensure_ascii=False, indent=2)
            elif format.lower() == 'csv':
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['title', 'url', 'depth', 'source', 'content_length'])
                    writer.writeheader()
                    for result in self.crawl_results:
                        writer.writerow(result)
            
            logger.info(f"결과 내보내기 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"결과 내보내기 실패: {e}")
    
    def close(self):
        """리소스 정리"""
        self.session.close()
