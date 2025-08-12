#!/usr/bin/env python3
"""
Requests + BeautifulSoup을 사용한 재귀 크롤링 서비스
"""

import asyncio
import json
import time
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import requests
from collections import deque

class RecursiveCrawlerService:
    """Requests + BeautifulSoup을 사용한 재귀 크롤링 서비스"""
    
    def __init__(self):
        self.max_pages = 50  # 최대 크롤링 페이지 수
        self.max_depth = 3   # 최대 크롤링 깊이
        self.delay = 1       # 요청 간 지연 시간 (초)
        
    async def crawl_website(self, start_url: str) -> List[Dict[str, Any]]:
        """웹사이트 크롤링 - 재귀적 방식"""
        try:
            print(f"재귀 크롤링 시작: {start_url}")
            
            # 동기 함수를 별도 스레드에서 실행
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self._crawl_sync, start_url)
            
            print(f"총 {len(results)}개 페이지 크롤링 완료")
            return results
            
        except Exception as e:
            print(f"재귀 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
            return await self._fallback_crawl(start_url)
    
    def _crawl_sync(self, start_url: str) -> List[Dict[str, Any]]:
        """동기적 재귀 크롤링"""
        results = []
        visited_urls = set()
        url_queue = deque([(start_url, 0)])  # (url, depth)
        base_domain = urlparse(start_url).netloc
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        while url_queue and len(results) < self.max_pages:
            current_url, depth = url_queue.popleft()
            
            # 이미 방문한 URL이거나 깊이 제한 초과
            if current_url in visited_urls or depth > self.max_depth:
                continue
                
            try:
                print(f"페이지 크롤링 중: {current_url} (깊이: {depth})")
                
                # 페이지 요청
                response = requests.get(current_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # HTML 파싱
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 페이지 정보 추출
                title = soup.find('title')
                title_text = title.get_text().strip() if title else "제목 없음"
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ""
                
                text_content = soup.get_text(separator=' ', strip=True)
                
                # 링크들 추출
                links = []
                new_urls = []
                
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if text and href:
                        full_url = urljoin(current_url, href)
                        links.append({
                            'text': text[:100],
                            'url': full_url
                        })
                        
                        # 같은 도메인의 새로운 URL을 큐에 추가
                        if (self._is_same_domain(base_domain, full_url) and 
                            self._is_valid_url(full_url) and
                            full_url not in visited_urls and
                            len(url_queue) < self.max_pages * 2):
                            
                            # URL 정규화 (프래그먼트 제거)
                            clean_url = full_url.split('#')[0]
                            if clean_url not in visited_urls:
                                new_urls.append((clean_url, depth + 1))
                                print(f"새로운 URL 추가: {clean_url}")
                
                # 기능 관련 키워드로 분석
                features = self._extract_features(title_text, text_content, description, links)
                
                page_result = {
                    'title': title_text,
                    'url': current_url,
                    'content': text_content[:2000] + "..." if len(text_content) > 2000 else text_content,
                    'description': description,
                    'links': links[:20],  # 최대 20개 링크만 저장
                    'features': features,
                    'depth': depth
                }
                
                results.append(page_result)
                visited_urls.add(current_url)
                
                # 새로운 URL들을 큐에 추가
                for url, new_depth in new_urls:
                    if url not in visited_urls:
                        url_queue.append((url, new_depth))
                
                # 요청 간 지연
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"페이지 처리 오류 ({current_url}): {e}")
                visited_urls.add(current_url)
                continue
        
        return results
    
    def _is_same_domain(self, base_domain: str, url: str) -> bool:
        """같은 도메인인지 확인"""
        try:
            url_domain = urlparse(url).netloc
            return base_domain == url_domain or url_domain.endswith(f".{base_domain}")
        except:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """유효한 URL인지 확인 (이미지, CSS, JS 파일 등 제외)"""
        try:
            parsed = urlparse(url)
            # 파일 확장자가 있는 경우 HTML 관련만 허용
            path = parsed.path.lower()
            if '.' in path:
                valid_extensions = ['.html', '.htm', '.php', '.asp', '.aspx', '.jsp', '.py']
                invalid_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.doc', '.docx', '.xml', '.json']
                
                # 유효한 확장자가 있으면 허용
                if any(path.endswith(ext) for ext in valid_extensions):
                    return True
                # 무효한 확장자가 있으면 제외
                if any(path.endswith(ext) for ext in invalid_extensions):
                    return False
                # 확장자가 없으면 허용 (일반 페이지)
                return True
            return True
        except:
            return False
    
    async def _fallback_crawl(self, url: str) -> List[Dict[str, Any]]:
        """fallback 크롤링"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "제목 없음"
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            text_content = soup.get_text(separator=' ', strip=True)
            
            links = []
            for link in soup.find_all('a', href=True)[:20]:
                href = link.get('href')
                text = link.get_text(strip=True)
                if text and href:
                    full_url = urljoin(url, href)
                    links.append({
                        'text': text[:100],
                        'url': full_url
                    })
            
            features = self._extract_features(title_text, text_content, description, links)
            
            return [{
                'title': title_text,
                'url': url,
                'content': text_content[:2000] + "..." if len(text_content) > 2000 else text_content,
                'description': description,
                'links': links,
                'features': features,
                'depth': 0
            }]
            
        except Exception as e:
            print(f"fallback 크롤링 오류 ({url}): {e}")
            return [{
                'title': '크롤링 실패',
                'url': url,
                'content': f'오류: {str(e)}',
                'description': '',
                'links': [],
                'features': [],
                'depth': 0
            }]
    
    def _extract_features(self, title: str, content: str, description: str, links: List[Dict]) -> List[Dict[str, Any]]:
        """기능 관련 키워드 추출"""
        feature_keywords = [
            '채팅', '메시지', '파일', '공유', '화상', '회의', '통화', '앱', '모바일', '봇', 'API',
            '보안', '설정', '알림', '검색', '백업', '동기화', '그룹', '채널', '워크스페이스',
            'chat', 'message', 'file', 'share', 'video', 'call', 'meeting', 'app', 'mobile', 'bot',
            'security', 'setting', 'notification', 'search', 'backup', 'sync', 'group', 'channel'
        ]
        
        features = []
        all_text = f"{title} {description} {content}".lower()
        
        for keyword in feature_keywords:
            if keyword.lower() in all_text:
                # 키워드 주변 텍스트 추출
                keyword_pos = all_text.find(keyword.lower())
                start = max(0, keyword_pos - 100)
                end = min(len(all_text), keyword_pos + 100)
                context = all_text[start:end].strip()
                
                features.append({
                    'keyword': keyword,
                    'context': context,
                    'title': title,
                    'category': '기능'
                })
        
        # 링크에서도 기능 찾기
        for link in links:
            link_text = link['text'].lower()
            for keyword in feature_keywords:
                if keyword.lower() in link_text:
                    features.append({
                        'keyword': keyword,
                        'context': link['text'],
                        'title': link['text'],
                        'category': '링크',
                        'url': link['url']
                    })
        
        return features[:10]  # 최대 10개만 반환

# 동기 래퍼 함수
def crawl_website_sync(start_url: str) -> List[Dict[str, Any]]:
    """동기적으로 웹사이트 크롤링"""
    return asyncio.run(RecursiveCrawlerService().crawl_website(start_url))

# 사용 예시
if __name__ == "__main__":
    # 테스트용 크롤링
    start_url = "https://example.com"
    results = crawl_website_sync(start_url)
    
    print(f"\n크롤링 완료! 총 {len(results)}개 페이지")
    for i, result in enumerate(results[:3]):  # 처음 3개만 출력
        print(f"\n--- 페이지 {i+1} ---")
        print(f"제목: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"깊이: {result['depth']}")
        print(f"기능: {len(result['features'])}개")
        print(f"링크: {len(result['links'])}개")
