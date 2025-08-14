#!/usr/bin/env python3
"""
Vertex AI 분석 테스트
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vertex_ai_analysis_service import VertexAIAnalysisService
from services.crawlee_crawler_service import RecursiveCrawlerService

async def test_vertex_ai_analysis():
    """Vertex AI 분석 테스트"""
    try:
        print("Vertex AI 분석 테스트 시작...")
        
        # 서비스 초기화
        vertex_ai_service = VertexAIAnalysisService()
        crawler_service = RecursiveCrawlerService()
        
        # 테스트 URL들
        competitor_url = "https://slack.com/help/articles/115004071768-What-is-Slack-"
        our_product_url = "https://support.discord.com/hc/en-us/articles/360045138571-Getting-Started"
        
        print(f"경쟁사 크롤링 시작: {competitor_url}")
        competitor_data = await crawler_service.crawl_website(competitor_url)
        print(f"경쟁사 크롤링 완료: {len(competitor_data)}개 페이지")
        
        print(f"우리 제품 크롤링 시작: {our_product_url}")
        our_product_data = await crawler_service.crawl_website(our_product_url)
        print(f"우리 제품 크롤링 완료: {len(our_product_data)}개 페이지")
        
        print("Vertex AI 분석 시작...")
        result = await vertex_ai_service.analyze_features(competitor_data, our_product_data)
        print("Vertex AI 분석 완료")
        
        print("\n=== 분석 결과 ===")
        print(f"성공 여부: {result.get('success', False)}")
        print(f"분석 방법: {result.get('analysis_method', 'unknown')}")
        
        if result.get('success'):
            competitor_features = result.get('competitor_features', {})
            our_product_features = result.get('our_product_features', {})
            
            print(f"\n경쟁사 기능 수: {competitor_features.get('analysis_summary', {}).get('total_features', 0)}")
            print(f"우리 제품 기능 수: {our_product_features.get('analysis_summary', {}).get('total_features', 0)}")
            
            # 경쟁사 기능들 출력
            print("\n=== 경쟁사 기능들 ===")
            for feature in competitor_features.get('extracted_features', [])[:5]:  # 처음 5개만
                print(f"- {feature.get('name', 'N/A')} ({feature.get('category', 'N/A')})")
            
            # 우리 제품 기능들 출력
            print("\n=== 우리 제품 기능들 ===")
            for feature in our_product_features.get('extracted_features', [])[:5]:  # 처음 5개만
                print(f"- {feature.get('name', 'N/A')} ({feature.get('category', 'N/A')})")
            
            # 비교 분석 결과
            comparison = result.get('comparison_analysis', {})
            summary = comparison.get('summary', {})
            print(f"\n=== 비교 분석 요약 ===")
            print(f"총 비교 가능 기능: {summary.get('total_comparable_features', 0)}")
            print(f"우리 고유 기능: {summary.get('our_unique_features', 0)}")
            print(f"경쟁사 고유 기능: {summary.get('competitor_unique_features', 0)}")
            print(f"전체 평가: {summary.get('overall_assessment', 'N/A')}")
            
        else:
            print(f"오류: {result.get('error', '알 수 없는 오류')}")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vertex_ai_analysis())

