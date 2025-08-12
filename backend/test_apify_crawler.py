#!/usr/bin/env python3
"""
Apify 크롤러 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.apify_crawler import run_apify_crawler, ApifyCrawlConfig

def test_apify_crawler():
    """Apify 크롤러 테스트"""
    print("Apify 크롤러 테스트 시작...")
    
    # 테스트 설정
    base_url = "https://httpbin.org/"
    project_id = 1
    
    # 기본 설정으로 테스트
    config = ApifyCrawlConfig(
        max_pages=5,
        max_depth=2,
        headless=True,
        timeout=10000
    )
    
    try:
        # 크롤링 실행
        results = run_apify_crawler(base_url, project_id, config)
        
        print(f"크롤링 완료: {len(results)}개 페이지")
        
        # 결과 출력
        for i, result in enumerate(results):
            print(f"\n--- 결과 {i+1} ---")
            print(f"URL: {result['url']}")
            print(f"제목: {result.get('title', 'N/A')}")
            print(f"상태: {result['status']}")
            print(f"콘텐츠 길이: {result['content_length']}")
            print(f"추출 방법: {result['extraction_method']}")
            
            if result.get('crawling_metadata'):
                metadata = result['crawling_metadata']
                print(f"메타데이터:")
                print(f"  - 제목: {metadata.get('title', 'N/A')}")
                print(f"  - 링크 수: {metadata.get('links_count', 0)}")
                print(f"  - 콘텐츠 길이: {metadata.get('content_length', 0)}")
        
        print("\n테스트 성공!")
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_apify_crawler()
