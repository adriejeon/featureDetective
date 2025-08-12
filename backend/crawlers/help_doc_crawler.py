"""
도움말 문서 크롤러
도움말 사이트에서 기능 정보를 크롤링하는 전용 크롤러
"""

import logging
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class HelpDocCrawler(BaseCrawler):
    """도움말 문서 크롤러"""
    
    def __init__(self, rate_limit: float = 1.0, timeout: int = 30, max_pages: int = 50):
        """
        도움말 문서 크롤러 초기화
        
        Args:
            rate_limit: 요청 간 대기 시간 (초)
            timeout: 요청 타임아웃 (초)
            max_pages: 최대 크롤링 페이지 수
        """
        super().__init__(rate_limit, timeout)
        self.max_pages = max_pages
        
        # 기능 관련 키워드 (확장)
        self.feature_keywords = {
            '채팅': ['chat', 'message', 'messaging', 'conversation', 'talk', 'communication'],
            '파일': ['file', 'document', 'attachment', 'upload', 'download', 'share'],
            '화상': ['video', 'call', 'meeting', 'conference', 'stream', 'record'],
            '봇': ['bot', 'chatbot', 'automation', 'workflow', 'integration'],
            '보안': ['security', 'privacy', 'encryption', 'authentication', 'permission'],
            '알림': ['notification', 'alert', 'reminder', 'push', 'email', 'sms'],
            '설정': ['setting', 'configuration', 'preference', 'option', 'customize'],
            '검색': ['search', 'find', 'filter', 'query', 'lookup', 'discover'],
            '백업': ['backup', 'sync', 'synchronization', 'export', 'import'],
            '분석': ['analytics', 'report', 'statistics', 'insight', 'data', 'metrics'],
            'AI': ['ai', 'artificial', 'intelligence', 'machine', 'learning', 'ml'],
            '대시보드': ['dashboard', 'panel', 'overview', 'monitor'],
            '지식': ['knowledge', 'guide', 'manual', 'tutorial', 'documentation'],
            '시작': ['getting', 'started', 'begin', 'setup', 'install'],
            '관리': ['manage', 'admin', 'control', 'manage'],
            '생성': ['create', 'make', 'build', 'generate'],
            '센터': ['center', 'centre', 'hub'],
            '구조': ['structure', 'organization', 'layout'],
            '기본': ['basic', 'default', 'standard', 'essential'],
        }
    
    def crawl(self, url: str) -> List[Dict[str, Any]]:
        """
        도움말 사이트 크롤링
        
        Args:
            url: 크롤링할 도움말 사이트 URL
            
        Returns:
            크롤링된 기능 데이터 리스트
        """
        logger.info(f"도움말 문서 크롤링 시작: {url}")
        
        try:
            # 메인 페이지 크롤링
            main_soup = self.get_page(url)
            if not main_soup:
                logger.error(f"메인 페이지 로드 실패: {url}")
                return []
            
            # 기능 관련 링크 찾기
            feature_links = self._find_feature_links(main_soup, url)
            logger.info(f"발견된 기능 링크 수: {len(feature_links)}")
            
            # 각 기능 페이지 크롤링
            features = []
            for i, link_info in enumerate(feature_links[:self.max_pages]):
                try:
                    logger.info(f"크롤링 중 ({i+1}/{min(self.max_pages, len(feature_links))}): {link_info['title']}")
                    
                    # 기능 페이지 크롤링
                    feature_content = self._crawl_feature_page(link_info['url'], link_info['title'])
                    if feature_content and len(feature_content) > 30:
                        features.append({
                            'title': link_info['title'],
                            'url': link_info['url'],
                            'content': feature_content,
                            'keywords': self._extract_keywords(feature_content),
                            'source_page': link_info.get('source_page', ''),
                            'category': self._categorize_feature(link_info['title'], feature_content)
                        })
                        logger.info(f"  ✓ 기능 크롤링 성공: {link_info['title']} ({len(feature_content)}자)")
                    
                    # 하위 페이지도 크롤링
                    sub_features = self._crawl_sub_pages(link_info['url'], link_info['title'])
                    if sub_features:
                        features.extend(sub_features)
                        logger.info(f"  ✓ 하위 페이지 {len(sub_features)}개 추가")
                        
                except Exception as e:
                    logger.error(f"  ✗ 페이지 크롤링 오류 ({link_info['url']}): {e}")
                    continue
            
            # 추가 페이지 크롤링 (사이트맵, 카테고리 등)
            additional_features = self._crawl_additional_pages(url, main_soup)
            if additional_features:
                features.extend(additional_features)
                logger.info(f"추가 페이지 {len(additional_features)}개 크롤링")
            
            logger.info(f"총 크롤링된 기능 수: {len(features)}")
            return features
            
        except Exception as e:
            logger.error(f"도움말 문서 크롤링 오류 ({url}): {e}")
            return []
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        도움말 페이지에서 콘텐츠 추출
        
        Args:
            soup: BeautifulSoup 객체
            url: 페이지 URL
            
        Returns:
            추출된 텍스트
        """
        # 불필요한 태그 제거
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            tag.decompose()
        
        # 메인 콘텐츠 영역 찾기
        content_selectors = [
            'main', 'article', '.content', '.main-content', '.post-content',
            '.entry-content', '.page-content', '.help-content', '.documentation'
        ]
        
        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break
        
        if not content_element:
            content_element = soup.find('body')
        
        # 텍스트 추출
        text = content_element.get_text() if content_element else soup.get_text()
        
        # 텍스트 정리
        text = self.clean_text(text)
        
        return text[:2000]  # 최대 2000자로 제한
    
    def _find_feature_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """기능 관련 링크 찾기"""
        feature_links = []
        
        # 모든 링크 찾기
        all_links = soup.find_all('a', href=True)
        logger.info(f"전체 링크 수: {len(all_links)}")
        
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
                    if self._is_feature_related(title) or self._is_feature_related(href):
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
    
    def _is_feature_related(self, text: str) -> bool:
        """텍스트가 기능 관련인지 확인"""
        text_lower = text.lower()
        
        # 기능 관련 키워드 확인
        for category, keywords in self.feature_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True
        
        # 도움말 관련 키워드
        help_keywords = ['help', 'guide', 'manual', 'tutorial', 'documentation', 'faq', 'support']
        if any(keyword in text_lower for keyword in help_keywords):
            return True
        
        # 2글자 이상의 단어는 기능 관련으로 간주 (더 관대하게)
        return len(text.strip()) >= 2
    
    def _crawl_feature_page(self, url: str, title: str) -> str:
        """단일 기능 페이지 크롤링"""
        try:
            soup = self.get_page(url)
            if not soup:
                return ""
            
            return self.extract_content(soup, url)
            
        except Exception as e:
            logger.error(f"기능 페이지 크롤링 오류 ({url}): {e}")
            return ""
    
    def _crawl_sub_pages(self, parent_url: str, parent_title: str) -> List[Dict[str, Any]]:
        """하위 페이지 크롤링"""
        sub_features = []
        
        try:
            soup = self.get_page(parent_url)
            if not soup:
                return sub_features
            
            # 하위 링크 찾기
            sub_links = soup.find_all('a', href=True)
            
            for link in sub_links[:10]:  # 최대 10개
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and title and len(title) > 3:
                    if href.startswith('/'):
                        full_url = urljoin(parent_url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    if self.is_same_domain(parent_url, full_url):
                        try:
                            content = self._crawl_feature_page(full_url, title)
                            if content and len(content) > 30:
                                sub_features.append({
                                    'title': title,
                                    'url': full_url,
                                    'content': content,
                                    'keywords': self._extract_keywords(content),
                                    'source_page': parent_title,
                                    'category': self._categorize_feature(title, content)
                                })
                        except Exception as e:
                            logger.error(f"하위 페이지 크롤링 오류 ({full_url}): {e}")
                            continue
            
        except Exception as e:
            logger.error(f"하위 페이지 크롤링 오류 ({parent_url}): {e}")
        
        return sub_features
    
    def _crawl_additional_pages(self, base_url: str, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """추가 페이지 크롤링 (사이트맵, 카테고리 등)"""
        additional_features = []
        
        # 사이트맵 링크 찾기
        sitemap_links = soup.find_all('a', href=re.compile(r'sitemap|map|index', re.I))
        
        for link in sitemap_links[:5]:  # 최대 5개
            href = link.get('href')
            if href:
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                if self.is_same_domain(base_url, full_url):
                    try:
                        content = self._crawl_feature_page(full_url, link.get_text(strip=True))
                        if content and len(content) > 30:
                            additional_features.append({
                                'title': link.get_text(strip=True),
                                'url': full_url,
                                'content': content,
                                'keywords': self._extract_keywords(content),
                                'source_page': '사이트맵',
                                'category': '기타'
                            })
                    except Exception as e:
                        logger.error(f"추가 페이지 크롤링 오류 ({full_url}): {e}")
                        continue
        
        return additional_features
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        keywords = []
        text_lower = text.lower()
        
        for category, category_keywords in self.feature_keywords.items():
            for keyword in category_keywords:
                if keyword in text_lower:
                    keywords.append(keyword)
        
        return list(set(keywords))  # 중복 제거
    
    def _categorize_feature(self, title: str, content: str) -> str:
        """기능 카테고리 분류"""
        text = f"{title} {content}".lower()
        
        for category, keywords in self.feature_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return '기타'
