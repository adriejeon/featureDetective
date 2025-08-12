#!/usr/bin/env python3
"""
강화된 크롤러 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.robust_crawler import RobustWebCrawler

def test_robust_crawler():
    """강화된 크롤러 테스트"""
    print("강화된 크롤러 테스트 시작...")
    
    try:
        # 강화된 크롤러 초기화
        crawler = RobustWebCrawler(rate_limit=1.0, timeout=30)
        print("✅ 강화된 크롤러 초기화 성공!")
        
        # 테스트 URL
        test_url = "https://docs.gelatto.ai/"
        print(f"테스트 URL: {test_url}")
        
        # 크롤링 실행
        print("\n크롤링 실행 중...")
        pages = crawler.crawl(test_url, max_pages=5)
        
        print(f"\n크롤링 결과: {len(pages)}개 페이지 발견")
        
        if pages:
            print("\n페이지 정보:")
            for i, page in enumerate(pages):
                print(f"  {i+1}. {page['title']}")
                print(f"     URL: {page['url']}")
                print(f"     내용 길이: {len(page['content'])}자")
                print(f"     내용 미리보기: {page['content'][:100]}...")
                print()
        else:
            print("❌ 페이지를 발견하지 못했습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ 강화된 크롤러 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_robust_crawler()
    if success:
        print("\n🎉 강화된 크롤러 테스트 성공!")
    else:
        print("\n💥 강화된 크롤러 테스트 실패!")
        sys.exit(1)
