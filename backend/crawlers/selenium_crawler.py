"""
Selenium 기반 강화된 웹 크롤러
JavaScript 기반 웹사이트를 크롤링할 수 있는 강화된 크롤러
"""

import time
import logging
from typing import Dict, Optional, List, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re # Added for regex matching

logger = logging.getLogger(__name__)


class SeleniumCrawler:
    """Selenium 기반 강화된 크롤러"""
    
    def __init__(self, rate_limit: float = 2.0, timeout: int = 30, headless: bool = True):
        """
        Selenium 크롤러 초기화
        
        Args:
            rate_limit: 요청 간 대기 시간 (초)
            timeout: 페이지 로드 타임아웃 (초)
            headless: 헤드리스 모드 사용 여부
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.headless = headless
        self.driver = None
        self.last_request_time = 0
        
        self._setup_driver()
    
    def _setup_driver(self):
        """Chrome 드라이버 설정"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # 성능 최적화 옵션
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # 불필요한 기능 비활성화
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # ChromeDriver 자동 설치 및 설정
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 스크립트 실행으로 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium 드라이버 초기화 성공")
            
        except Exception as e:
            logger.error(f"Selenium 드라이버 초기화 실패: {e}")
            self.driver = None
    
    def _rate_limit(self):
        """요청 간 대기 시간 적용"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Selenium으로 웹페이지 가져오기
        
        Args:
            url: 가져올 URL
            
        Returns:
            페이지 정보 딕셔너리 또는 None
        """
        if not self.driver:
            logger.error("Selenium 드라이버가 초기화되지 않았습니다.")
            return None
        
        try:
            self._rate_limit()
            logger.info(f"Selenium 크롤링 시작: {url}")
            
            # 페이지 로드
            self.driver.get(url)
            
            # 페이지 로드 대기
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # JavaScript 실행 완료 대기
            time.sleep(3)
            
            # 페이지 정보 추출
            title = self.driver.title
            page_source = self.driver.page_source
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(page_source, 'html.parser')
            
            logger.info(f"페이지 로드 성공: {title}")
            
            return {
                'url': url,
                'title': title,
                'content': page_source,
                'soup': soup,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Selenium 크롤링 실패 ({url}): {e}")
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
        a 태그를 기반으로 기능 링크 찾기 (JavaScript 동적 로드 포함)
        
        Args:
            soup: BeautifulSoup 객체
            base_url: 기준 URL
            
        Returns:
            기능 관련 링크 리스트
        """
        feature_links = []
        
        try:
            # 모든 a 태그 찾기
            all_links = soup.find_all('a', href=True)
            logger.info(f"전체 a 태그 수: {len(all_links)}")
            
            # 링크 정보 출력 (디버깅용)
            for i, link in enumerate(all_links[:10]):  # 처음 10개만 출력
                href = link.get('href')
                title = link.get_text(strip=True)
                logger.info(f"링크 {i+1}: '{title}' -> {href}")
            
            for link in all_links:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                # 링크가 유효하고 제목이 있는 경우
                if href and title and len(title) > 2 and len(title) < 200:
                    # 상대 URL을 절대 URL로 변환
                    if href.startswith('/'):
                        full_url = urljoin(base_url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin(base_url, href)
                    
                    # 같은 도메인인지 확인
                    if self.is_same_domain(base_url, full_url):
                        # a 태그의 텍스트를 기능명으로 인식
                        feature_links.append({
                            'title': title,
                            'url': full_url,
                            'source_page': base_url,
                            'type': 'link'
                        })
                        logger.info(f"기능 링크 발견: {title} -> {full_url}")
            
            # 중복 제거
            unique_links = []
            seen_urls = set()
            for link in feature_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            logger.info(f"기능 관련 링크 수: {len(unique_links)}")
            return unique_links
            
        except Exception as e:
            logger.error(f"기능 링크 찾기 실패: {e}")
            return []
    
    def find_feature_links_with_selenium(self, driver, base_url: str) -> List[Dict[str, str]]:
        """
        Selenium을 사용하여 JavaScript로 동적 로드되는 링크들 찾기
        
        Args:
            driver: Selenium WebDriver
            base_url: 기준 URL
            
        Returns:
            기능 관련 링크 리스트
        """
        feature_links = []
        
        try:
            # JavaScript로 모든 링크 정보 가져오기 (더 상세한 정보)
            links_info = driver.execute_script("""
                var links = document.querySelectorAll('a[href]');
                var result = [];
                for (var i = 0; i < links.length; i++) {
                    var link = links[i];
                    var href = link.getAttribute('href');
                    var title = link.textContent.trim();
                    var isVisible = link.offsetWidth > 0 && link.offsetHeight > 0;
                    var parentClasses = '';
                    var parentTag = '';
                    var linkClasses = link.className || '';
                    var linkId = link.id || '';
                    
                    if (link.parentElement) {
                        parentClasses = link.parentElement.className || '';
                        parentTag = link.parentElement.tagName;
                    }
                    
                    // 부모 요소들의 클래스 정보도 수집
                    var ancestorClasses = [];
                    var current = link.parentElement;
                    var depth = 0;
                    while (current && depth < 5) {
                        if (current.className) {
                            ancestorClasses.push(current.className);
                        }
                        current = current.parentElement;
                        depth++;
                    }
                    
                    result.push({
                        href: href,
                        title: title,
                        isVisible: isVisible,
                        parentClasses: parentClasses,
                        parentTag: parentTag,
                        linkClasses: linkClasses,
                        linkId: linkId,
                        ancestorClasses: ancestorClasses
                    });
                }
                return result;
            """)
            
            logger.info(f"Selenium으로 {len(links_info)}개 링크 발견")
            
            # 디버깅을 위해 처음 20개 링크 정보 출력
            for i, link_info in enumerate(links_info[:20]):
                logger.info(f"링크 {i+1}: '{link_info['title']}' -> {link_info['href']} (가시성: {link_info['isVisible']}, 부모: {link_info['parentTag']}, 클래스: {link_info['parentClasses']})")
            
            for link_info in links_info:
                href = link_info['href']
                title = link_info['title']
                is_visible = link_info['isVisible']
                parent_classes = link_info['parentClasses']
                parent_tag = link_info['parentTag']
                link_classes = link_info['linkClasses']
                ancestor_classes = link_info['ancestorClasses']
                
                # 링크가 유효하고 제목이 있는 경우
                if href and title and len(title) > 2 and len(title) < 200:
                    # 상대 URL을 절대 URL로 변환
                    if href.startswith('/'):
                        full_url = urljoin(base_url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin(base_url, href)
                    
                    # 같은 도메인인지 확인
                    if self.is_same_domain(base_url, full_url):
                        # a 태그의 텍스트를 기능명으로 인식
                        feature_links.append({
                            'title': title,
                            'url': full_url,
                            'source_page': base_url,
                            'type': 'selenium_link',
                            'visible': is_visible,
                            'parent_classes': parent_classes,
                            'parent_tag': parent_tag,
                            'link_classes': link_classes,
                            'ancestor_classes': ancestor_classes
                        })
                        logger.info(f"Selenium 링크 발견: {title} -> {full_url} (가시성: {is_visible})")
            
            # 중복 제거
            unique_links = []
            seen_urls = set()
            for link in feature_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            logger.info(f"Selenium 기능 관련 링크 수: {len(unique_links)}")
            return unique_links
            
        except Exception as e:
            logger.error(f"Selenium 링크 찾기 실패: {e}")
            return []
    
    def find_gitbook_sidebar_links(self, driver, base_url: str) -> List[Dict[str, str]]:
        """
        GitBook 기반 웹사이트의 사이드바 메뉴 링크 찾기
        
        Args:
            driver: Selenium WebDriver
            base_url: 기준 URL
            
        Returns:
            사이드바 메뉴 링크 리스트
        """
        sidebar_links = []
        
        try:
            # GitBook 사이드바 구조 탐지
            sidebar_selectors = [
                'nav[class*="sidebar"]',
                'div[class*="sidebar"]',
                'aside[class*="sidebar"]',
                'nav[class*="navigation"]',
                'div[class*="navigation"]',
                'ul[class*="menu"]',
                'nav[class*="menu"]',
                'div[class*="menu"]',
                '[data-testid*="sidebar"]',
                '[data-testid*="navigation"]',
                '.css-1q9qplj',  # GitBook 특정 클래스
                '.css-1wrcrhn',  # GitBook 특정 클래스
                '.css-1d0b8xb',  # GitBook 특정 클래스
            ]
            
            for selector in sidebar_selectors:
                try:
                    elements = driver.find_elements('css selector', selector)
                    if elements:
                        logger.info(f"사이드바 요소 발견: {selector}")
                        for element in elements:
                            # 해당 요소 내의 모든 링크 찾기
                            links = element.find_elements('tag name', 'a')
                            for link in links:
                                try:
                                    href = link.get_attribute('href')
                                    title = link.text.strip()
                                    
                                    if href and title and len(title) > 2 and len(title) < 100:
                                        # 같은 도메인인지 확인
                                        if self.is_same_domain(base_url, href):
                                            sidebar_links.append({
                                                'title': title,
                                                'url': href,
                                                'source_page': base_url,
                                                'type': 'sidebar_menu',
                                                'selector': selector
                                            })
                                            logger.info(f"사이드바 메뉴 발견: {title} -> {href}")
                                except Exception as e:
                                    continue
                except Exception as e:
                    continue
            
            # JavaScript로 직접 사이드바 탐지
            js_sidebar_links = driver.execute_script("""
                var sidebarLinks = [];
                
                // GitBook 특정 구조 탐지
                var selectors = [
                    'nav[class*="sidebar"] a[href]',
                    'div[class*="sidebar"] a[href]',
                    'aside[class*="sidebar"] a[href]',
                    'nav[class*="navigation"] a[href]',
                    'div[class*="navigation"] a[href]',
                    'ul[class*="menu"] a[href]',
                    'nav[class*="menu"] a[href]',
                    'div[class*="menu"] a[href]',
                    '.css-1q9qplj a[href]',
                    '.css-1wrcrhn a[href]',
                    '.css-1d0b8xb a[href]'
                ];
                
                for (var i = 0; i < selectors.length; i++) {
                    var links = document.querySelectorAll(selectors[i]);
                    for (var j = 0; j < links.length; j++) {
                        var link = links[j];
                        var href = link.getAttribute('href');
                        var title = link.textContent.trim();
                        
                        if (href && title && title.length > 2 && title.length < 100) {
                            sidebarLinks.push({
                                href: href,
                                title: title,
                                selector: selectors[i]
                            });
                        }
                    }
                }
                
                return sidebarLinks;
            """)
            
            logger.info(f"JavaScript로 {len(js_sidebar_links)}개 사이드바 링크 발견")
            
            for link_info in js_sidebar_links:
                href = link_info['href']
                title = link_info['title']
                selector = link_info['selector']
                
                if href and title:
                    # 같은 도메인인지 확인
                    if self.is_same_domain(base_url, href):
                        sidebar_links.append({
                            'title': title,
                            'url': href,
                            'source_page': base_url,
                            'type': 'js_sidebar_menu',
                            'selector': selector
                        })
                        logger.info(f"JavaScript 사이드바 메뉴 발견: {title} -> {href}")
            
            # 중복 제거
            unique_links = []
            seen_urls = set()
            for link in sidebar_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            logger.info(f"사이드바 메뉴 링크 수: {len(unique_links)}")
            return unique_links
            
        except Exception as e:
            logger.error(f"사이드바 링크 찾기 실패: {e}")
            return []
    
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
    
    def extract_features_from_content(self, soup: BeautifulSoup, page_title: str) -> List[Dict[str, str]]:
        """
        페이지 내용에서 실제 기능들을 추출
        
        Args:
            soup: BeautifulSoup 객체
            page_title: 페이지 제목
            
        Returns:
            추출된 기능 리스트
        """
        features = []
        
        try:
            # FAQ 페이지에서 질문-답변 형태로 기능 추출
            if 'faq' in page_title.lower() or '질문' in page_title.lower():
                # FAQ 형태의 기능 추출
                questions = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
                
                for question in questions:
                    question_text = question.get_text(strip=True)
                    if question_text and len(question_text) > 5 and len(question_text) < 200:
                        # 답변 내용 찾기
                        answer = ""
                        next_element = question.find_next_sibling()
                        if next_element:
                            answer = next_element.get_text(strip=True)
                            if len(answer) > 20:  # 최소 20자 이상
                                features.append({
                                    'title': question_text,
                                    'description': answer[:300] + "..." if len(answer) > 300 else answer,
                                    'type': 'faq'
                                })
            
            # 일반 페이지에서 기능 추출
            else:
                # 제목 태그들에서 기능 추출
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                
                for heading in headings:
                    heading_text = heading.get_text(strip=True)
                    if heading_text and len(heading_text) > 3 and len(heading_text) < 150:
                        # 기능 관련 키워드가 포함된 제목만 선택
                        feature_keywords = [
                            '기능', '특징', '장점', '장치', '도구', '시스템', '서비스', '솔루션',
                            '관리', '설정', '생성', '편집', '분석', '보고', '모니터링', '통계',
                            '보안', '인증', '권한', '백업', '동기화', '내보내기', '가져오기',
                            '알림', '메시지', '채팅', '통신', '파일', '문서', '미디어',
                            '검색', '필터', '정렬', '그룹화', '분류', '태그', '라벨'
                        ]
                        
                        if any(keyword in heading_text for keyword in feature_keywords):
                            # 다음 단락에서 설명 찾기
                            description = ""
                            next_element = heading.find_next_sibling()
                            if next_element and next_element.name in ['p', 'div', 'span']:
                                description = next_element.get_text(strip=True)
                                if len(description) > 20:
                                    features.append({
                                        'title': heading_text,
                                        'description': description[:300] + "..." if len(description) > 300 else description,
                                        'type': 'feature'
                                    })
            
            # 리스트 형태의 기능들 추출
            lists = soup.find_all(['ul', 'ol'])
            for list_elem in lists:
                list_items = list_elem.find_all('li')
                for item in list_items:
                    item_text = item.get_text(strip=True)
                    if item_text and len(item_text) > 5 and len(item_text) < 200:
                        # 기능 관련 키워드가 포함된 항목만 선택
                        if any(keyword in item_text.lower() for keyword in [
                            '기능', '특징', '지원', '제공', '사용', '설정', '관리', '생성'
                        ]):
                            features.append({
                                'title': item_text,
                                'description': f"{item_text} 기능을 제공합니다.",
                                'type': 'list_item'
                            })
            
            logger.info(f"페이지에서 {len(features)}개 기능 추출: {page_title}")
            return features
            
        except Exception as e:
            logger.error(f"기능 추출 실패: {e}")
            return []
    
    def crawl(self, url: str, max_pages: int = 20) -> List[Dict[str, Any]]:
        """
        웹사이트 크롤링 - a 태그 기반 기능 추출
        
        Args:
            url: 크롤링할 URL
            max_pages: 최대 페이지 수
            
        Returns:
            크롤링된 페이지 리스트
        """
        logger.info(f"Selenium 크롤링 시작: {url}")
        
        try:
            # 메인 페이지 크롤링
            main_page = self.fetch_page(url)
            if not main_page:
                logger.error(f"메인 페이지 크롤링 실패: {url}")
                return []
            
            pages = [{
                'title': main_page['title'] or '메인 페이지',
                'url': url,
                'content': self.extract_clean_text(main_page['soup']),
                'source_page': '',
                'features': []
            }]
            
            # 강력한 CSS 선택자로 모든 a 태그 탐지
            if self.driver:
                all_feature_links = self.find_all_links_with_advanced_selectors(self.driver, url)
                logger.info(f"고급 선택자로 {len(all_feature_links)}개 링크 발견")
                
                # 각 링크의 페이지 내용을 크롤링하여 기능 정보 생성
                feature_pages = []
                for i, link_info in enumerate(all_feature_links[:max_pages-1]):
                    try:
                        logger.info(f"기능 페이지 크롤링 ({i+1}/{min(max_pages-1, len(all_feature_links))}): {link_info['title']}")
                        
                        # 각 링크 페이지의 내용을 추출
                        feature_content = self.extract_page_content_for_feature(
                            self.driver, 
                            link_info['url'], 
                            link_info['title']
                        )
                        
                        if feature_content['content_length'] > 30:  # 최소 30자 이상
                            feature_pages.append({
                                'title': link_info['title'],
                                'url': link_info['url'],
                                'content': feature_content['content'],
                                'description': feature_content['description'],
                                'source_page': link_info['source_page'],
                                'features': [{
                                    'title': link_info['title'],
                                    'description': feature_content['description'],
                                    'type': 'link_page'
                                }]
                            })
                            logger.info(f"  ✅ 기능 페이지 크롤링 성공: {link_info['title']} ({feature_content['content_length']}자)")
                        else:
                            logger.info(f"  ⚠️ 페이지 내용 부족: {link_info['title']} ({feature_content['content_length']}자)")
                    
                    except Exception as e:
                        logger.error(f"  ❌ 기능 페이지 크롤링 실패 ({link_info['url']}): {e}")
                        continue
                
                # 메인 페이지와 기능 페이지들을 합치기
                pages.extend(feature_pages)
                logger.info(f"총 {len(pages)}개 페이지 크롤링 완료")
                
                return pages
            
            # 각 기능 페이지 크롤링
            for i, link_info in enumerate(feature_links[:max_pages-1]):
                try:
                    logger.info(f"기능 페이지 크롤링 ({i+1}/{min(max_pages-1, len(feature_links))}): {link_info['title']}")
                    
                    page = self.fetch_page(link_info['url'])
                    if page:
                        clean_content = self.extract_clean_text(page['soup'])
                        if len(clean_content) > 30:  # 최소 30자 이상
                            # 페이지에서 기능 정보 추출
                            features = self.extract_features_from_content(page['soup'], link_info['title'])
                            
                            pages.append({
                                'title': link_info['title'],
                                'url': link_info['url'],
                                'content': clean_content,
                                'source_page': link_info['source_page'],
                                'features': features
                            })
                            logger.info(f"  ✅ 페이지 크롤링 성공: {link_info['title']} ({len(clean_content)}자, {len(features)}개 세부기능)")
                        else:
                            logger.info(f"  ⚠️ 페이지 내용 부족: {link_info['title']} ({len(clean_content)}자)")
                    
                except Exception as e:
                    logger.error(f"  ❌ 페이지 크롤링 실패 ({link_info['url']}): {e}")
                    continue
            
            logger.info(f"크롤링 완료: {len(pages)}개 페이지")
            return pages
            
        except Exception as e:
            logger.error(f"크롤링 실패: {e}")
            return []
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium 드라이버 종료")
    
    def __del__(self):
        """소멸자에서 드라이버 종료"""
        self.close()

    def find_all_links_with_advanced_selectors(self, driver, base_url: str) -> List[Dict[str, str]]:
        """
        강력한 CSS 선택자를 사용하여 모든 a 태그 탐지
        
        Args:
            driver: Selenium WebDriver
            base_url: 기준 URL
            
        Returns:
            발견된 모든 링크 리스트
        """
        all_links = []
        
        try:
            # 다양한 CSS 선택자로 a 태그 탐지
            selectors = [
                'a[href]',  # 기본 a 태그
                'a[href*="/"]',  # 상대 경로가 있는 a 태그
                'a[href^="/"]',  # 절대 경로로 시작하는 a 태그
                'a[href^="http"]',  # 외부 링크
                'nav a[href]',  # 네비게이션 내 a 태그
                'aside a[href]',  # 사이드바 내 a 태그
                'ul a[href]',  # 리스트 내 a 태그
                'li a[href]',  # 리스트 아이템 내 a 태그
                'div a[href]',  # div 내 a 태그
                'section a[href]',  # 섹션 내 a 태그
                'main a[href]',  # 메인 영역 내 a 태그
                'header a[href]',  # 헤더 내 a 태그
                'footer a[href]',  # 푸터 내 a 태그
                '[class*="menu"] a[href]',  # 메뉴 클래스가 포함된 요소 내 a 태그
                '[class*="nav"] a[href]',  # 네비게이션 클래스가 포함된 요소 내 a 태그
                '[class*="sidebar"] a[href]',  # 사이드바 클래스가 포함된 요소 내 a 태그
                '[class*="link"] a[href]',  # 링크 클래스가 포함된 요소 내 a 태그
                '[data-testid*="link"] a[href]',  # data-testid에 link가 포함된 요소 내 a 태그
                '[role="navigation"] a[href]',  # 네비게이션 역할을 가진 요소 내 a 태그
                '[role="menuitem"] a[href]',  # 메뉴 아이템 역할을 가진 요소 내 a 태그
            ]
            
            seen_urls = set()
            
            for selector in selectors:
                try:
                    # JavaScript로 해당 선택자의 모든 링크 정보 가져오기
                    links_info = driver.execute_script(f"""
                        var links = document.querySelectorAll('{selector}');
                        var result = [];
                        for (var i = 0; i < links.length; i++) {{
                            var link = links[i];
                            var href = link.getAttribute('href');
                            var title = link.textContent.trim();
                            var isVisible = link.offsetWidth > 0 && link.offsetHeight > 0;
                            var parentClasses = '';
                            var parentTag = '';
                            var linkClasses = link.className || '';
                            var linkId = link.id || '';
                            
                            if (link.parentElement) {{
                                parentClasses = link.parentElement.className || '';
                                parentTag = link.parentElement.tagName;
                            }}
                            
                            result.push({{
                                href: href,
                                title: title,
                                isVisible: isVisible,
                                parentClasses: parentClasses,
                                parentTag: parentTag,
                                linkClasses: linkClasses,
                                linkId: linkId,
                                selector: '{selector}'
                            }});
                        }}
                        return result;
                    """)
                    
                    logger.info(f"선택자 '{selector}'로 {len(links_info)}개 링크 발견")
                    
                    for link_info in links_info:
                        href = link_info['href']
                        title = link_info['title']
                        is_visible = link_info['isVisible']
                        parent_classes = link_info['parentClasses']
                        parent_tag = link_info['parentTag']
                        link_classes = link_info['linkClasses']
                        selector_used = link_info['selector']
                        
                        # 링크가 유효하고 제목이 있는 경우
                        if href and title and len(title) > 2 and len(title) < 200:
                            # 상대 URL을 절대 URL로 변환
                            if href.startswith('/'):
                                full_url = urljoin(base_url, href)
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                full_url = urljoin(base_url, href)
                            
                            # 같은 도메인인지 확인하고 중복 제거
                            if self.is_same_domain(base_url, full_url) and full_url not in seen_urls:
                                seen_urls.add(full_url)
                                all_links.append({
                                    'title': title,
                                    'url': full_url,
                                    'source_page': base_url,
                                    'type': 'advanced_selector',
                                    'visible': is_visible,
                                    'parent_classes': parent_classes,
                                    'parent_tag': parent_tag,
                                    'link_classes': link_classes,
                                    'selector_used': selector_used
                                })
                                logger.info(f"고급 선택자로 링크 발견: {title} -> {full_url} (선택자: {selector_used})")
                
                except Exception as e:
                    logger.error(f"선택자 '{selector}' 실행 중 오류: {e}")
                    continue
            
            logger.info(f"총 {len(all_links)}개 고유 링크 발견")
            return all_links
            
        except Exception as e:
            logger.error(f"고급 선택자 링크 찾기 실패: {e}")
            return []
    
    def extract_page_content_for_feature(self, driver, url: str, feature_title: str) -> Dict[str, str]:
        """
        기능 페이지의 내용을 추출하여 기능 설명 생성
        
        Args:
            driver: Selenium WebDriver
            url: 페이지 URL
            feature_title: 기능명
            
        Returns:
            기능 정보 딕셔너리
        """
        try:
            logger.info(f"기능 페이지 내용 추출: {feature_title} -> {url}")
            
            # 페이지 로드
            driver.get(url)
            time.sleep(2)  # 페이지 로드 대기
            
            # 페이지 정보 추출
            page_title = driver.title
            page_source = driver.page_source
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 깨끗한 텍스트 추출
            clean_text = self.extract_clean_text(soup)
            
            # 기능 설명 생성 (페이지 내용을 요약)
            if len(clean_text) > 50:
                # 첫 300자 정도를 설명으로 사용
                description = clean_text[:300]
                if len(clean_text) > 300:
                    description += "..."
            else:
                description = f"{feature_title} 기능에 대한 상세 정보를 제공합니다."
            
            return {
                'title': feature_title,
                'url': url,
                'page_title': page_title,
                'content': clean_text,
                'description': description,
                'content_length': len(clean_text)
            }
            
        except Exception as e:
            logger.error(f"페이지 내용 추출 실패 ({url}): {e}")
            return {
                'title': feature_title,
                'url': url,
                'page_title': '',
                'content': '',
                'description': f"{feature_title} 기능에 대한 정보를 제공합니다.",
                'content_length': 0
            }
