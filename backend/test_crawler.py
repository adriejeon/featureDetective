#!/usr/bin/env python3
"""
크롤러 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.help_doc_crawler import HelpDocCrawler
import requests
from bs4 import BeautifulSoup

def test_crawler():
    """크롤러 테스트"""
    print("크롤러 테스트 시작...")
    
    try:
        # 먼저 직접 웹페이지 접근 테스트
        test_url = "https://docs.gelatto.ai/"
        print(f"직접 웹페이지 접근 테스트: {test_url}")
        
        response = requests.get(test_url, timeout=10)
        print(f"HTTP 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"페이지 제목: {soup.title.string if soup.title else 'N/A'}")
            
            # 모든 링크 찾기
            all_links = soup.find_all('a', href=True)
            print(f"전체 링크 수: {len(all_links)}")
            
            # 처음 10개 링크 출력
            for i, link in enumerate(all_links[:10]):
                href = link.get('href')
                title = link.get_text(strip=True)
                print(f"  {i+1}. {title} -> {href}")
        
        print("\n" + "="*50)
        print("크롤러 테스트 시작...")
        
        # 크롤러 초기화
        crawler = HelpDocCrawler(rate_limit=1.0, timeout=30, max_pages=5)
        print("✅ 크롤러 초기화 성공!")
        
        # _find_feature_links 메서드 직접 테스트
        print("\n기능 링크 찾기 테스트...")
        feature_links = crawler._find_feature_links(soup, test_url)
        print(f"발견된 기능 링크 수: {len(feature_links)}")
        
        for i, link in enumerate(feature_links[:5]):
            print(f"  {i+1}. {link['title']} -> {link['url']}")
        
        # 크롤링 실행
        pages = crawler.crawl(test_url)
        
        print(f"\n크롤링 결과: {len(pages)}개 페이지 발견")
        
        if pages:
            print("첫 번째 페이지 내용:")
            print(f"제목: {pages[0].get('title', 'N/A')}")
            print(f"URL: {pages[0].get('url', 'N/A')}")
            print(f"내용 길이: {len(pages[0].get('content', ''))}자")
            print(f"내용 미리보기: {pages[0].get('content', '')[:200]}...")
        else:
            print("❌ 페이지를 발견하지 못했습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ 크롤러 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crawler()
    if success:
        print("\n🎉 크롤러 테스트 성공!")
    else:
        print("\n💥 크롤러 테스트 실패!")
        sys.exit(1)
