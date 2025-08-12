#!/usr/bin/env python3
"""
고급 크롤러 간단 테스트 스크립트
순환 import 문제를 피하기 위해 크롤러만 테스트합니다.
"""

import sys
import os
import time
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.advanced_site_crawler import AdvancedSiteCrawler, CrawlConfig


def test_basic_crawling():
    """기본 크롤링 테스트"""
    print("=== 기본 크롤링 테스트 ===")
    
    # 기본 설정으로 크롤러 생성
    config = CrawlConfig(
        max_pages=3,
        max_depth=1,
        rate_limit=1.0,
        timeout=30
    )
    
    crawler = AdvancedSiteCrawler(config)
    
    try:
        # 테스트 URL (간단한 웹사이트)
        test_url = "https://httpbin.org/"
        
        print(f"크롤링 시작: {test_url}")
        results = crawler.crawl(test_url)
        
        print(f"크롤링 완료: {len(results)}개 페이지")
        
        # 결과 출력
        for i, result in enumerate(results):
            print(f"\n--- 페이지 {i+1} ---")
            print(f"제목: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"깊이: {result['depth']}")
            print(f"소스: {result['source']}")
            print(f"콘텐츠 길이: {result['content_length']}자")
            print(f"콘텐츠 미리보기: {result['content'][:200]}...")
        
        # 통계 출력
        stats = crawler.get_crawl_stats()
        print(f"\n=== 크롤링 통계 ===")
        print(f"총 페이지: {stats['total_pages']}")
        print(f"성공: {stats['successful_pages']}")
        print(f"실패: {stats['failed_pages']}")
        if stats.get('duration'):
            print(f"소요 시간: {stats['duration']:.2f}초")
        
    except Exception as e:
        print(f"크롤링 중 오류: {e}")
    finally:
        crawler.close()


def test_help_center_crawling():
    """헬프 센터 크롤링 테스트"""
    print("\n=== 헬프 센터 크롤링 테스트 ===")
    
    # 헬프 센터 설정
    config = CrawlConfig(
        max_pages=5,
        max_depth=2,
        include_patterns=[
            '*/help/*', '*/support/*', '*/docs/*', '*/guide/*',
            '*/manual/*', '*/tutorial/*', '*/faq/*', '*/knowledge/*'
        ],
        exclude_patterns=[
            '*.pdf', '*.doc', '*.docx', '*.zip', '*.rar',
            'mailto:', 'tel:', 'javascript:',
            '/admin/', '/login/', '/logout/', '/register/',
            '?utm_', '?fbclid', '?gclid'
        ]
    )
    
    crawler = AdvancedSiteCrawler(config)
    
    try:
        # 간단한 테스트 URL
        test_url = "https://httpbin.org/"
        
        print(f"헬프 센터 크롤링 시작: {test_url}")
        results = crawler.crawl(test_url)
        
        print(f"크롤링 완료: {len(results)}개 페이지")
        
        # 결과 요약
        for i, result in enumerate(results):
            print(f"\n--- 페이지 {i+1} ---")
            print(f"제목: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"콘텐츠 길이: {result['content_length']}자")
        
    except Exception as e:
        print(f"헬프 센터 크롤링 중 오류: {e}")
    finally:
        crawler.close()


def test_custom_settings():
    """사용자 정의 설정 테스트"""
    print("\n=== 사용자 정의 설정 테스트 ===")
    
    # 사용자 정의 설정
    config = CrawlConfig(
        max_pages=3,
        max_depth=1,
        include_patterns=['*/about/*', '*/features/*', '*/pricing/*'],
        exclude_patterns=['*.pdf', 'mailto:', 'tel:', 'javascript:'],
        css_exclude_selectors=['nav', 'footer', 'header', '.ads', '.banner']
    )
    
    crawler = AdvancedSiteCrawler(config)
    
    try:
        # 간단한 웹사이트 테스트
        test_url = "https://httpbin.org/"
        
        print(f"사용자 정의 설정 크롤링 시작: {test_url}")
        results = crawler.crawl(test_url)
        
        print(f"크롤링 완료: {len(results)}개 페이지")
        
        # 결과 요약
        for i, result in enumerate(results):
            print(f"\n--- 페이지 {i+1} ---")
            print(f"제목: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"콘텐츠 길이: {result['content_length']}자")
        
    except Exception as e:
        print(f"사용자 정의 설정 크롤링 중 오류: {e}")
    finally:
        crawler.close()


def test_export_results():
    """결과 내보내기 테스트"""
    print("\n=== 결과 내보내기 테스트 ===")
    
    config = CrawlConfig(max_pages=2, max_depth=1)
    crawler = AdvancedSiteCrawler(config)
    
    try:
        test_url = "https://httpbin.org/"
        results = crawler.crawl(test_url)
        
        # JSON으로 내보내기
        json_file = "test_crawl_results.json"
        crawler.export_results(json_file, 'json')
        print(f"JSON 결과 내보내기 완료: {json_file}")
        
        # CSV로 내보내기
        csv_file = "test_crawl_results.csv"
        crawler.export_results(csv_file, 'csv')
        print(f"CSV 결과 내보내기 완료: {csv_file}")
        
        # 파일 크기 확인
        if Path(json_file).exists():
            size = Path(json_file).stat().st_size
            print(f"JSON 파일 크기: {size} bytes")
        
        if Path(csv_file).exists():
            size = Path(csv_file).stat().st_size
            print(f"CSV 파일 크기: {size} bytes")
        
    except Exception as e:
        print(f"결과 내보내기 중 오류: {e}")
    finally:
        crawler.close()


def test_config_creation():
    """설정 생성 테스트"""
    print("\n=== 설정 생성 테스트 ===")
    
    # 기본 설정
    config1 = CrawlConfig()
    print("기본 설정:")
    print(f"  최대 페이지: {config1.max_pages}")
    print(f"  최대 깊이: {config1.max_depth}")
    print(f"  요청 간격: {config1.rate_limit}초")
    print(f"  타임아웃: {config1.timeout}초")
    print(f"  하위 도메인 탐색: {config1.follow_subdomains}")
    print(f"  Sitemap 사용: {config1.use_sitemap}")
    print(f"  robots.txt 준수: {config1.respect_robots_txt}")
    
    # 사용자 정의 설정
    config2 = CrawlConfig(
        max_pages=50,
        max_depth=4,
        rate_limit=2.0,
        include_patterns=['*/help/*', '*/docs/*'],
        exclude_patterns=['*.pdf', 'mailto:'],
        css_exclude_selectors=['nav', 'footer']
    )
    
    print("\n사용자 정의 설정:")
    print(f"  최대 페이지: {config2.max_pages}")
    print(f"  최대 깊이: {config2.max_depth}")
    print(f"  요청 간격: {config2.rate_limit}초")
    print(f"  포함 패턴: {config2.include_patterns}")
    print(f"  제외 패턴: {config2.exclude_patterns}")
    print(f"  CSS 제외 선택자: {config2.css_exclude_selectors}")


def main():
    """메인 테스트 함수"""
    print("고급 크롤러 간단 테스트 시작")
    print("=" * 50)
    
    # 각 테스트 실행
    test_config_creation()
    test_basic_crawling()
    test_help_center_crawling()
    test_custom_settings()
    test_export_results()
    
    print("\n" + "=" * 50)
    print("모든 테스트 완료!")


if __name__ == "__main__":
    main()
