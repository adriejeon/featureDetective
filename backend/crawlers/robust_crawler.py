"""
강화된 웹 크롤러
인코딩 문제와 다양한 웹사이트 구조를 처리할 수 있는 강화된 크롤러
"""

import requests
import chardet
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin, urlparse
from typing import Dict, Optional, List, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re

logger = logging.getLogger(__name__)


class RobustWebCrawler:
    """강화된 웹 크롤러"""
    
    def __init__(self, rate_limit: float = 1.0, timeout: int = 30):
        """
        강화된 크롤러 초기화
        
        Args:
            rate_limit: 요청 간 대기 시간 (초)
            timeout: 요청 타임아웃 (초)
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.last_request_time = 0
        
        # 강화된 세션 설정
        self.session = requests.Session()
        
        # 재시도 전략 설정
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 강화된 헤더 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def _rate_limit(self):
        """요청 간 대기 시간 적용"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def detect_encoding(self, content: bytes) -> str:
        """
        콘텐츠의 인코딩을 감지
        
        Args:
            content: 바이너리 콘텐츠
            
        Returns:
            감지된 인코딩
        """
        # chardet로 인코딩 감지
        detected = chardet.detect(content)
        
        if detected['confidence'] > 0.7:
            return detected['encoding']
        
        # 감지 실패 시 일반적인 인코딩들 시도
        common_encodings = ['utf-8', 'euc-kr', 'cp949', 'iso-8859-1', 'ascii']
        
        for encoding in common_encodings:
            try:
                content.decode(encoding)
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 마지막 수단으로 UTF-8 사용
        return 'utf-8'
    
    def fetch_with_encoding_fix(self, url: str) -> Optional[Dict[str, Any]]:
        """
        인코딩 문제를 해결하여 웹페이지 가져오기
        
        Args:
            url: 가져올 URL
            
        Returns:
            페이지 정보 딕셔너리 또는 None
        """
        try:
            self._rate_limit()
            logger.info(f"강화된 크롤링 시작: {url}")
            
            # HTTP 요청
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 인코딩 감지 및 수정
            encoding = self.detect_encoding(response.content)
            logger.info(f"감지된 인코딩: {encoding}")
            
            # 텍스트 디코딩
            try:
                text = response.content.decode(encoding, errors='ignore')
            except Exception as e:
                logger.warning(f"인코딩 실패, UTF-8로 재시도: {e}")
                text = response.content.decode('utf-8', errors='ignore')
            
            # BeautifulSoup 파싱
            soup = BeautifulSoup(text, 'html.parser')
            
            # 페이지 정보 반환
            return {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'content': text,
                'soup': soup,
                'encoding': encoding,
                'status_code': response.status_code,
                'content_length': len(response.content)
            }
            
        except requests.RequestException as e:
            logger.error(f"HTTP 요청 실패 ({url}): {e}")
            return None
        except Exception as e:
            logger.error(f"크롤링 실패 ({url}): {e}")
            return None
    
    def extract_clean_text(self, soup: BeautifulSoup) -> str:
        """
        깨끗한 텍스트 추출
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            정리된 텍스트
        """
        # 불필요한 요소 제거
        unwanted_elements = [
            'script', 'style', 'nav', 'footer', 'header', 
            'aside', 'noscript', 'iframe', 'embed', 'object',
            'meta', 'link', 'title', 'head'
        ]
        
        for element in soup(unwanted_elements):
            element.decompose()
        
        # 텍스트 추출
        text = soup.get_text()
        
        # 텍스트 정리
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line and len(line) > 2:  # 2글자 이상만 포함
                lines.append(line)
        
        return '\n'.join(lines)
    
    def find_feature_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        기능 관련 링크 찾기
        
        Args:
            soup: BeautifulSoup 객체
            base_url: 기준 URL
            
        Returns:
            기능 관련 링크 리스트
        """
        feature_links = []
        
        # 모든 링크 찾기
        all_links = soup.find_all('a', href=True)
        logger.info(f"전체 링크 수: {len(all_links)}")
        
        # 기능 관련 키워드
        feature_keywords = [
            'guide', 'help', 'manual', 'tutorial', 'documentation', 'faq', 'support',
            'dashboard', 'panel', 'overview', 'monitor', 'manage', 'admin', 'control',
            'create', 'make', 'build', 'generate', 'setup', 'install', 'configure',
            'knowledge', 'center', 'hub', 'structure', 'organization', 'layout',
            'basic', 'default', 'standard', 'essential', 'feature', 'function'
        ]
        
        for link in all_links:
            href = link.get('href')
            title = link.get_text(strip=True)
            
            if href and title and len(title) > 2 and len(title) < 150:
                # 상대 URL을 절대 URL로 변환
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(base_url, href)
                
                # 같은 도메인인지 확인
                if self.is_same_domain(base_url, full_url):
                    # 기능 관련 키워드가 포함된 링크만 선택
                    title_lower = title.lower()
                    href_lower = href.lower()
                    
                    if any(keyword in title_lower or keyword in href_lower for keyword in feature_keywords):
                        feature_links.append({
                            'title': title,
                            'url': full_url,
                            'source_page': base_url
                        })
        
        # 중복 제거
        unique_links = []
        seen_urls = set()
        for link in feature_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        logger.info(f"기능 관련 링크 수: {len(unique_links)}")
        return unique_links
    
    def is_same_domain(self, base_url: str, target_url: str) -> bool:
        """
        같은 도메인인지 확인
        
        Args:
            base_url: 기준 URL
            target_url: 확인할 URL
            
        Returns:
            같은 도메인이면 True
        """
        try:
            base_domain = urlparse(base_url).netloc
            target_domain = urlparse(target_url).netloc
            
            # 같은 도메인이거나 하위 도메인인 경우
            return base_domain in target_domain or target_domain in base_domain
        except Exception:
            return False
    
    def crawl(self, url: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        웹사이트 크롤링
        
        Args:
            url: 크롤링할 URL
            max_pages: 최대 페이지 수
            
        Returns:
            크롤링된 페이지 리스트
        """
        logger.info(f"강화된 크롤링 시작: {url}")
        
        try:
            # 메인 페이지 크롤링
            main_page = self.fetch_with_encoding_fix(url)
            if not main_page:
                logger.error(f"메인 페이지 크롤링 실패: {url}")
                return []
            
            pages = [{
                'title': main_page['title'] or '메인 페이지',
                'url': url,
                'content': self.extract_clean_text(main_page['soup']),
                'source_page': ''
            }]
            
            # 기능 관련 링크 찾기
            feature_links = self.find_feature_links(main_page['soup'], url)
            
            # 각 기능 페이지 크롤링
            for i, link_info in enumerate(feature_links[:max_pages-1]):
                try:
                    logger.info(f"기능 페이지 크롤링 ({i+1}/{min(max_pages-1, len(feature_links))}): {link_info['title']}")
                    
                    page = self.fetch_with_encoding_fix(link_info['url'])
                    if page:
                        clean_content = self.extract_clean_text(page['soup'])
                        if len(clean_content) > 50:  # 최소 50자 이상
                            pages.append({
                                'title': link_info['title'],
                                'url': link_info['url'],
                                'content': clean_content,
                                'source_page': link_info['source_page']
                            })
                            logger.info(f"  ✅ 페이지 크롤링 성공: {link_info['title']} ({len(clean_content)}자)")
                    
                except Exception as e:
                    logger.error(f"  ❌ 페이지 크롤링 실패 ({link_info['url']}): {e}")
                    continue
            
            logger.info(f"크롤링 완료: {len(pages)}개 페이지")
            return pages
            
        except Exception as e:
            logger.error(f"크롤링 실패: {e}")
            return []
