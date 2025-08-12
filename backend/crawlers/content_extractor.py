"""
콘텐츠 추출기
웹 페이지에서 깨끗한 텍스트 콘텐츠를 추출하는 모듈
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
from readability import Document

logger = logging.getLogger(__name__)


class ContentExtractor:
    """콘텐츠 추출기"""
    
    def __init__(self):
        """콘텐츠 추출기 초기화"""
        # 제거할 태그들
        self.remove_tags = [
            'script', 'style', 'nav', 'footer', 'header', 'aside', 
            'iframe', 'noscript', 'meta', 'link', 'form', 'button',
            'input', 'select', 'textarea', 'label', 'fieldset'
        ]
        
        # 제거할 클래스/ID 패턴
        self.remove_patterns = [
            r'navigation', r'menu', r'sidebar', r'footer', r'header',
            r'breadcrumb', r'pagination', r'comment', r'advertisement',
            r'popup', r'modal', r'overlay', r'tooltip', r'cookie'
        ]
        
        # 우선순위가 높은 콘텐츠 선택자
        self.content_selectors = [
            'main', 'article', '.content', '.main-content', '.post-content',
            '.entry-content', '.page-content', '.help-content', '.documentation',
            '.article-content', '.text-content', '.body-content'
        ]
    
    def extract_content(self, html_content: str, url: str) -> Dict[str, str]:
        """
        HTML에서 콘텐츠 추출
        
        Args:
            html_content: HTML 콘텐츠
            url: 페이지 URL
            
        Returns:
            추출된 콘텐츠 정보
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 기본 정리
            self._clean_html(soup)
            
            # 메인 콘텐츠 찾기
            main_content = self._find_main_content(soup)
            
            if main_content:
                # 메인 콘텐츠에서 텍스트 추출
                text = self._extract_text_from_element(main_content)
            else:
                # 전체 페이지에서 텍스트 추출
                text = self._extract_text_from_element(soup)
            
            # 텍스트 정리
            cleaned_text = self._clean_text(text)
            
            return {
                'title': self._extract_title(soup),
                'content': cleaned_text,
                'url': url,
                'content_length': len(cleaned_text)
            }
            
        except Exception as e:
            logger.error(f"콘텐츠 추출 오류 ({url}): {e}")
            return {
                'title': '',
                'content': '',
                'url': url,
                'content_length': 0
            }
    
    def _clean_html(self, soup: BeautifulSoup):
        """HTML 정리"""
        # 불필요한 태그 제거
        for tag_name in self.remove_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # 불필요한 요소 제거 (클래스/ID 패턴 기반)
        for pattern in self.remove_patterns:
            for element in soup.find_all(class_=re.compile(pattern, re.I)):
                element.decompose()
            for element in soup.find_all(id=re.compile(pattern, re.I)):
                element.decompose()
        
        # 빈 태그 제거
        for tag in soup.find_all():
            if len(tag.get_text(strip=True)) == 0:
                tag.decompose()
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """메인 콘텐츠 영역 찾기"""
        # 우선순위 선택자로 메인 콘텐츠 찾기
        for selector in self.content_selectors:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > 100:
                return element
        
        # body 태그에서 가장 큰 텍스트 블록 찾기
        body = soup.find('body')
        if body:
            # 텍스트가 많은 요소 찾기
            text_elements = []
            for element in body.find_all(['div', 'section', 'article', 'main']):
                text_length = len(element.get_text(strip=True))
                if text_length > 200:  # 최소 200자 이상
                    text_elements.append((element, text_length))
            
            if text_elements:
                # 텍스트가 가장 많은 요소 반환
                text_elements.sort(key=lambda x: x[1], reverse=True)
                return text_elements[0][0]
        
        return None
    
    def _extract_text_from_element(self, element: Tag) -> str:
        """요소에서 텍스트 추출"""
        # 모든 텍스트 추출
        text = element.get_text()
        
        # 줄바꿈 정리
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                lines.append(line)
        
        return '\n'.join(lines)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """페이지 제목 추출"""
        # title 태그에서 제목 추출
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            if title:
                return title
        
        # h1 태그에서 제목 추출
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text(strip=True)
            if title:
                return title
        
        return ''
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 불필요한 공백 제거
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                # 연속된 공백 제거
                line = re.sub(r'\s+', ' ', line)
                lines.append(line)
        
        # 빈 줄 제거
        cleaned_lines = []
        for line in lines:
            if line:
                cleaned_lines.append(line)
        
        # 텍스트 결합
        cleaned_text = '\n'.join(cleaned_lines)
        
        # 최종 정리
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)  # 연속된 줄바꿈 정리
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    def extract_links(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        """
        HTML에서 링크 추출
        
        Args:
            html_content: HTML 콘텐츠
            base_url: 기준 URL
            
        Returns:
            링크 정보 리스트
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and title:
                    # 상대 URL을 절대 URL로 변환
                    if href.startswith('/'):
                        full_url = f"{base_url.rstrip('/')}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
                    
                    links.append({
                        'url': full_url,
                        'title': title,
                        'text': title
                    })
            
            return links
            
        except Exception as e:
            logger.error(f"링크 추출 오류 ({base_url}): {e}")
            return []
    
    def extract_metadata(self, html_content: str) -> Dict[str, str]:
        """
        HTML에서 메타데이터 추출
        
        Args:
            html_content: HTML 콘텐츠
            
        Returns:
            메타데이터 딕셔너리
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            metadata = {}
            
            # meta 태그에서 메타데이터 추출
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                
                if name and content:
                    metadata[name] = content
            
            # Open Graph 메타데이터
            og_data = {}
            for meta in soup.find_all('meta', property=re.compile(r'^og:')):
                property_name = meta.get('property', '').replace('og:', '')
                content = meta.get('content', '')
                if property_name and content:
                    og_data[property_name] = content
            
            if og_data:
                metadata['og_data'] = og_data
            
            return metadata
            
        except Exception as e:
            logger.error(f"메타데이터 추출 오류: {e}")
            return {}
    
    def extract_structure(self, html_content: str) -> Dict[str, List[str]]:
        """
        HTML 구조 추출 (제목, 섹션 등)
        
        Args:
            html_content: HTML 콘텐츠
            
        Returns:
            구조 정보 딕셔너리
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            structure = {
                'headings': [],
                'sections': [],
                'lists': []
            }
            
            # 제목 추출
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = heading.get_text(strip=True)
                if text:
                    structure['headings'].append({
                        'level': heading.name,
                        'text': text
                    })
            
            # 섹션 추출
            for section in soup.find_all(['section', 'article', 'main', 'div']):
                title = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if title:
                    structure['sections'].append({
                        'title': title.get_text(strip=True),
                        'tag': section.name,
                        'content_length': len(section.get_text(strip=True))
                    })
            
            # 리스트 추출
            for ul in soup.find_all(['ul', 'ol']):
                items = []
                for li in ul.find_all('li'):
                    text = li.get_text(strip=True)
                    if text:
                        items.append(text)
                
                if items:
                    structure['lists'].append({
                        'type': ul.name,
                        'items': items
                    })
            
            return structure
            
        except Exception as e:
            logger.error(f"구조 추출 오류: {e}")
            return {'headings': [], 'sections': [], 'lists': []}
