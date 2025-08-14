#!/usr/bin/env python3
"""
개선된 크롤링 서비스 - 텍스트 길이 제한, 중복 제거, 효율적 처리
"""

import asyncio
import json
import time
import hashlib
from typing import List, Dict, Any, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import requests
from collections import deque
import httpx
import asyncio
from readability import Document
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecursiveCrawlerService:
    """개선된 크롤링 서비스"""
    
    def __init__(self):
        self.max_pages = 10  # 최대 크롤링 페이지 수 (줄임)
        self.max_depth = 1   # 최대 크롤링 깊이 (줄임)
        self.delay = 1.0     # 요청 간 지연 시간 (늘림 - 429 오류 방지)
        self.max_text_length = 1500  # 최대 텍스트 길이 (줄임)
        self.similarity_threshold = 0.8  # 중복 제거 임계값
        self.processed_hashes: Set[str] = set()  # 중복 제거용 해시
        
        # NLTK 데이터 다운로드
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
    async def crawl_website(self, start_url: str) -> List[Dict[str, Any]]:
        """웹사이트 크롤링 - 개선된 방식"""
        try:
            print(f"개선된 크롤링 시작: {start_url}")
            
            # 동기 함수를 별도 스레드에서 실행
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self._crawl_sync, start_url)
            
            # 중복 제거 및 텍스트 길이 제한
            results = self._deduplicate_and_limit(results)
            
            print(f"총 {len(results)}개 페이지 크롤링 완료 (중복 제거 후)")
            return results
            
        except Exception as e:
            print(f"크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
            return await self._fallback_crawl(start_url)
    
    def _crawl_sync(self, start_url: str) -> List[Dict[str, Any]]:
        """동기적 크롤링 - 개선된 방식"""
        results = []
        visited_urls = set()
        url_queue = deque([(start_url, 0)])  # (url, depth)
        base_domain = urlparse(start_url).netloc
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        while url_queue and len(results) < self.max_pages:
            current_url, depth = url_queue.popleft()
            
            # 이미 방문한 URL이거나 깊이 제한 초과
            if current_url in visited_urls or depth > self.max_depth:
                continue
                
            try:
                print(f"페이지 크롤링 중: {current_url} (깊이: {depth})")
                
                # 페이지 요청 (타임아웃 증가)
                response = requests.get(current_url, headers=headers, timeout=20)
                response.raise_for_status()
                
                # HTML 파싱 및 본문 추출
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Readability를 사용한 본문 추출
                doc = Document(response.text)
                main_content = doc.summary()
                
                # 본문에서 텍스트 추출
                content_soup = BeautifulSoup(main_content, 'html.parser')
                text_content = content_soup.get_text(separator=' ', strip=True)
                
                # 텍스트 길이 제한
                text_content = self._limit_text_length(text_content)
                
                # 페이지 정보 추출
                title = soup.find('title')
                title_text = title.get_text().strip() if title else "제목 없음"
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ""
                
                # 결과 저장
                if text_content and len(text_content) > 100:  # 최소 길이 체크
                    results.append({
                        'url': current_url,
                        'title': title_text,
                        'description': description,
                        'content': text_content,
                        'depth': depth
                    })
                
                visited_urls.add(current_url)
                
                # 링크들 추출 (도움말 관련 링크 우선)
                if depth < self.max_depth:
                    new_urls = self._extract_helpful_links(soup, current_url, base_domain)
                    for url in new_urls:
                        if url not in visited_urls and len(url_queue) < self.max_pages * 2:
                            url_queue.append((url, depth + 1))
                
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"페이지 크롤링 실패: {current_url}, 오류: {e}")
                continue
        
        return results
    
    def _extract_helpful_links(self, soup: BeautifulSoup, current_url: str, base_domain: str) -> List[str]:
        """도움말 관련 링크 우선 추출"""
        helpful_urls = []
        all_urls = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True).lower()
            
            if href and text:
                full_url = urljoin(current_url, href)
                
                # 같은 도메인 체크
                if not self._is_same_domain(base_domain, full_url):
                    continue
                
                # 도움말 관련 링크 우선
                if any(keyword in text or keyword in href.lower() for keyword in 
                       ['help', 'guide', 'docs', 'documentation', 'faq', 'support', 'tutorial', 'manual']):
                    helpful_urls.append(full_url)
                else:
                    all_urls.append(full_url)
        
        # 도움말 링크를 먼저 반환, 그 다음 일반 링크
        return helpful_urls + all_urls[:5]  # 일반 링크는 최대 5개만
    
    def _limit_text_length(self, text: str) -> str:
        """텍스트 길이 제한"""
        if len(text) <= self.max_text_length:
            return text
        
        # 문장 단위로 자르기
        sentences = sent_tokenize(text)
        result = ""
        
        for sentence in sentences:
            if len(result + sentence) <= self.max_text_length:
                result += sentence + " "
            else:
                break
        
        return result.strip()
    
    def _deduplicate_and_limit(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """중복 제거 및 길이 제한"""
        if not results:
            return results
        
        # TF-IDF를 사용한 유사도 계산
        texts = [result['content'] for result in results]
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # 중복 제거
            unique_results = []
            for i, result in enumerate(results):
                is_duplicate = False
                
                for j, existing_result in enumerate(unique_results):
                    if similarity_matrix[i][j] > self.similarity_threshold:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_results.append(result)
            
            # 결과 수 제한
            return unique_results[:self.max_pages]
            
        except Exception as e:
            print(f"중복 제거 오류: {e}")
            return results[:self.max_pages]
    
    def _is_same_domain(self, base_domain: str, url: str) -> bool:
        """같은 도메인인지 확인"""
        try:
            parsed = urlparse(url)
            return parsed.netloc == base_domain
        except:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """유효한 URL인지 확인"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except:
            return False
    
    async def _fallback_crawl(self, start_url: str) -> List[Dict[str, Any]]:
        """폴백 크롤링 - 간단한 방식"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(start_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 간단한 텍스트 추출
            text_content = soup.get_text(separator=' ', strip=True)
            text_content = self._limit_text_length(text_content)
            
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "제목 없음"
            
            return [{
                'url': start_url,
                'title': title_text,
                'description': '',
                'content': text_content,
                'depth': 0
            }]
            
        except Exception as e:
            print(f"폴백 크롤링 실패: {e}")
            return []

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
