#!/usr/bin/env python3
"""
크롤링 문제 디버깅 도구
"""

import requests
import chardet
from bs4 import BeautifulSoup
import sys

def debug_crawling_issue(url: str):
    """크롤링 문제 디버깅"""
    print(f"🔍 URL 디버깅: {url}")
    print("="*50)
    
    try:
        # 1. 기본 요청
        print("1️⃣ HTTP 요청 시도...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"   ✅ HTTP 상태 코드: {response.status_code}")
        print(f"   📄 응답 크기: {len(response.content)} bytes")
        
        # 2. 인코딩 분석
        print("\n2️⃣ 인코딩 분석...")
        print(f"   🏷️  서버 인코딩: {response.encoding}")
        
        # chardet로 인코딩 감지
        detected = chardet.detect(response.content)
        print(f"   🔍 감지된 인코딩: {detected}")
        
        # 3. 다양한 인코딩으로 텍스트 추출 시도
        print("\n3️⃣ 인코딩별 텍스트 추출 테스트...")
        
        encodings_to_try = ['utf-8', 'euc-kr', 'cp949', 'iso-8859-1', 'ascii']
        
        for encoding in encodings_to_try:
            try:
                text = response.content.decode(encoding, errors='ignore')
                print(f"   ✅ {encoding}: {len(text)}자 (처음 100자: {text[:100].replace(chr(10), ' ').replace(chr(13), ' ')})")
            except Exception as e:
                print(f"   ❌ {encoding}: 실패 - {e}")
        
        # 4. BeautifulSoup 파싱 테스트
        print("\n4️⃣ BeautifulSoup 파싱 테스트...")
        
        # UTF-8로 시도
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else "제목 없음"
            print(f"   📄 페이지 제목: {title}")
            
            # 링크 수 확인
            links = soup.find_all('a', href=True)
            print(f"   🔗 링크 수: {len(links)}")
            
            # 처음 5개 링크 출력
            for i, link in enumerate(links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"      {i+1}. {text} -> {href}")
                
        except Exception as e:
            print(f"   ❌ BeautifulSoup 파싱 실패: {e}")
        
        # 5. 텍스트 내용 분석
        print("\n5️⃣ 텍스트 내용 분석...")
        try:
            # 불필요한 요소 제거
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            text = soup.get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            print(f"   📝 텍스트 라인 수: {len(lines)}")
            print(f"   📝 첫 5줄:")
            for i, line in enumerate(lines[:5]):
                print(f"      {i+1}. {line}")
                
        except Exception as e:
            print(f"   ❌ 텍스트 분석 실패: {e}")
        
        print("\n" + "="*50)
        print("✅ 디버깅 완료!")
        
    except Exception as e:
        print(f"❌ 디버깅 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://docs.gelatto.ai/"
    
    debug_crawling_issue(url)

