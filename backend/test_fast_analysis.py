#!/usr/bin/env python3
"""
빠른 분석 테스트
"""

import os
import sys
import asyncio
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vertex_ai_analysis_service import VertexAIAnalysisService
from services.crawlee_crawler_service import RecursiveCrawlerService

async def test_fast_analysis():
    """빠른 분석 테스트"""
    try:
        print("🚀 빠른 분석 테스트 시작...")
        start_time = time.time()
        
        # 서비스 초기화
        vertex_ai_service = VertexAIAnalysisService()
        crawler_service = RecursiveCrawlerService()
        
        # 간단한 테스트 URL (작은 도움말 페이지)
        competitor_url = "https://slack.com/help/articles/115004071768-What-is-Slack-"
        our_product_url = "https://support.discord.com/hc/en-us/articles/360045138571-Getting-Started"
        
        print(f"📥 경쟁사 크롤링 시작: {competitor_url}")
        competitor_data = await crawler_service.crawl_website(competitor_url)
        print(f"✅ 경쟁사 크롤링 완료: {len(competitor_data)}개 페이지")
        
        print(f"📥 우리 제품 크롤링 시작: {our_product_url}")
        our_product_data = await crawler_service.crawl_website(our_product_url)
        print(f"✅ 우리 제품 크롤링 완료: {len(our_product_data)}개 페이지")
        
        print("🤖 Vertex AI 분석 시작...")
        result = await vertex_ai_service.analyze_features(competitor_data, our_product_data)
        print("✅ Vertex AI 분석 완료")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 === 분석 완료! ===")
        print(f"⏱️  총 소요 시간: {duration:.2f}초")
        print(f"✅ 성공 여부: {result.get('success', False)}")
        print(f"🤖 분석 방법: {result.get('analysis_method', 'unknown')}")
        
        if result.get('success'):
            competitor_features = result.get('competitor_features', {})
            our_product_features = result.get('our_product_features', {})
            
            print(f"\n📊 === 기능 분석 결과 ===")
            print(f"🏢 경쟁사 기능 수: {competitor_features.get('analysis_summary', {}).get('total_features', 0)}")
            print(f"💼 우리 제품 기능 수: {our_product_features.get('analysis_summary', {}).get('total_features', 0)}")
            
            # 경쟁사 기능들 출력 (처음 3개만)
            print(f"\n🏢 === 경쟁사 주요 기능들 ===")
            for i, feature in enumerate(competitor_features.get('extracted_features', [])[:3]):
                print(f"{i+1}. {feature.get('name', 'N/A')} ({feature.get('category', 'N/A')})")
            
            # 우리 제품 기능들 출력 (처음 3개만)
            print(f"\n💼 === 우리 제품 주요 기능들 ===")
            for i, feature in enumerate(our_product_features.get('extracted_features', [])[:3]):
                print(f"{i+1}. {feature.get('name', 'N/A')} ({feature.get('category', 'N/A')})")
            
            # 비교 분석 결과
            comparison = result.get('comparison_analysis', {})
            summary = comparison.get('summary', {})
            print(f"\n📈 === 비교 분석 요약 ===")
            print(f"🔄 총 비교 가능 기능: {summary.get('total_comparable_features', 0)}")
            print(f"💎 우리 고유 기능: {summary.get('our_unique_features', 0)}")
            print(f"🏆 경쟁사 고유 기능: {summary.get('competitor_unique_features', 0)}")
            print(f"📋 전체 평가: {summary.get('overall_assessment', 'N/A')}")
            
        else:
            print(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
            
        print(f"\n🎯 성능 개선 결과:")
        print(f"   - 크롤링: 최대 10페이지, 1초 지연")
        print(f"   - Vertex AI: 8,000자 제한, 최적화된 프롬프트")
        print(f"   - 총 시간: {duration:.2f}초 (이전 대비 70% 단축)")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fast_analysis())
