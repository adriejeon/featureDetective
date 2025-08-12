#!/usr/bin/env python3
"""
간단한 크롤링 테스트 스크립트
"""

import requests
from bs4 import BeautifulSoup
import time

def test_simple_crawling():
    """간단한 크롤링 테스트"""
    url = "https://help.slack.com"
    
    print(f"크롤링 테스트 시작: {url}")
    
    try:
        # 기본 requests로 테스트
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 헤더: {dict(response.headers)}")
        print(f"콘텐츠 길이: {len(response.text)}")
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 제목 추출
        title = soup.find('title')
        if title:
            print(f"페이지 제목: {title.get_text().strip()}")
        
        # 메타 설명 추출
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            print(f"메타 설명: {meta_desc.get('content', '')}")
        
        # 링크 추출 (처음 10개)
        links = soup.find_all('a', href=True)[:10]
        print(f"발견된 링크 수: {len(soup.find_all('a', href=True))}")
        print("처음 10개 링크:")
        for i, link in enumerate(links):
            href = link.get('href')
            text = link.get_text().strip()[:50]
            print(f"  {i+1}. {text} -> {href}")
        
        # 텍스트 콘텐츠 추출 (처음 500자)
        text_content = soup.get_text()
        print(f"텍스트 콘텐츠 (처음 500자): {text_content[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"크롤링 오류: {e}")
        return False

if __name__ == "__main__":
    test_simple_crawling()
