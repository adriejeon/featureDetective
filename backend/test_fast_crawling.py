#!/usr/bin/env python3
"""
빠른 크롤링 테스트
"""

import os
import sys
import asyncio
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.crawlee_crawler_service import RecursiveCrawlerService

async def test_fast_crawling():
    """빠른 크롤링 테스트"""
    try:
        print("빠른 크롤링 테스트 시작...")
        start_time = time.time()
        
        crawler = RecursiveCrawlerService()
        
        # 테스트 URL (작은 도움말 페이지)
        test_url = "https://www.braze.com/docs/ko/help/help_articles/"
        
        print(f"크롤링 시작: {test_url}")
        results = await crawler.crawl_website(test_url)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n=== 크롤링 결과 ===")
        print(f"총 소요 시간: {duration:.2f}초")
        print(f"크롤링된 페이지 수: {len(results)}")
        
        for i, result in enumerate(results[:5], 1):  # 처음 5개만 표시
            print(f"{i}. {result['title']} ({len(result['content'])}자)")
            print(f"   URL: {result['url']}")
            print()
        
        return results
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_fast_crawling())

