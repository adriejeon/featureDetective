#!/usr/bin/env python3
"""
Selenium 크롤러 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.selenium_crawler import SeleniumCrawler

def test_selenium_crawler():
    """Selenium 크롤러 테스트"""
    print("Selenium 크롤러 테스트 시작...")
    
    crawler = None
    try:
        # Selenium 크롤러 초기화
        crawler = SeleniumCrawler(rate_limit=2.0, timeout=30, headless=True)
        print("✅ Selenium 크롤러 초기화 성공!")
        
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
                print(f"     내용 미리보기: {page['content'][:200]}...")
                
                # 기능 정보 표시
                if 'features' in page and page['features']:
                    print(f"     추출된 기능 수: {len(page['features'])}개")
                    for j, feature in enumerate(page['features'][:3]):  # 최대 3개만 표시
                        print(f"       - {feature['title']}")
                        print(f"         설명: {feature['description'][:100]}...")
                else:
                    print("     추출된 기능: 없음")
                print()
        else:
            print("❌ 페이지를 발견하지 못했습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ Selenium 크롤러 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    success = test_selenium_crawler()
    if success:
        print("\n🎉 Selenium 크롤러 테스트 성공!")
    else:
        print("\n💥 Selenium 크롤러 테스트 실패!")
        sys.exit(1)
