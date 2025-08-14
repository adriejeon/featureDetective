#!/usr/bin/env python3
"""
개선된 기능 탐지 서비스 테스트
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.feature_detection_service import FeatureDetectionService

async def test_feature_detection():
    """개선된 기능 탐지 테스트"""
    try:
        print("개선된 기능 탐지 테스트 시작...")
        
        # 서비스 초기화
        feature_service = FeatureDetectionService()
        
        # 테스트 URL들
        competitor_urls = ["https://slack.com/help/articles/115004071768-What-is-Slack-"]
        our_product_urls = ["https://support.discord.com/hc/en-us/articles/360045138571-Getting-Started"]
        
        print(f"경쟁사 URL: {competitor_urls}")
        print(f"우리 제품 URL: {our_product_urls}")
        
        # 기능 탐지 실행
        result = await feature_service.detect_features_from_urls(
            competitor_urls, 
            our_product_urls,
            "테스트 프로젝트"
        )
        
        print("\n=== 기능 탐지 결과 ===")
        print(f"성공 여부: {not result.get('error')}")
        
        if result.get('error'):
            print(f"오류: {result['error']}")
            return
        
        # 프로젝트 정보
        project_info = result.get('project_info', {})
        print(f"프로젝트명: {project_info.get('name', 'N/A')}")
        print(f"처리 시간: {project_info.get('processing_time_seconds', 0):.2f}초")
        print(f"총 제품 수: {project_info.get('total_products', 0)}")
        print(f"크롤링된 페이지 수: {project_info.get('total_pages_crawled', 0)}")
        
        # 분석 결과
        analysis_results = result.get('analysis_results', {})
        product_features = analysis_results.get('product_features', {})
        merged_features = analysis_results.get('merged_features', [])
        product_feature_mapping = analysis_results.get('product_feature_mapping', {})
        
        print(f"\n=== 기능 분석 결과 ===")
        print(f"통합된 고유 기능 수: {len(merged_features)}")
        
        # 각 제품별 기능 수
        for product_name, features in product_features.items():
            feature_count = len(features.get('extracted_features', []))
            print(f"{product_name}: {feature_count}개 기능")
        
        # 통합된 기능 목록 (처음 10개만)
        print(f"\n=== 통합된 기능 목록 (처음 10개) ===")
        for i, feature in enumerate(merged_features[:10]):
            print(f"{i+1}. {feature.get('name', 'N/A')} ({feature.get('category', 'N/A')})")
        
        # 제품별 기능 매핑 결과
        print(f"\n=== 제품별 기능 매핑 결과 ===")
        for product_name, feature_mapping in product_feature_mapping.items():
            print(f"\n{product_name}:")
            supported_count = 0
            total_count = len(feature_mapping)
            
            for feature_name, mapping_info in feature_mapping.items():
                status = mapping_info.get('status', 'X')
                if status == 'O':
                    supported_count += 1
                    print(f"  ✓ {feature_name}")
                else:
                    print(f"  ✗ {feature_name}")
            
            print(f"  지원률: {supported_count}/{total_count} ({supported_count/total_count*100:.1f}%)")
        
        # 요약
        summary = result.get('summary', {})
        print(f"\n=== 요약 ===")
        print(f"총 고유 기능: {summary.get('total_unique_features', 0)}")
        print(f"분석된 제품 수: {summary.get('total_products_analyzed', 0)}")
        print(f"분석 품질: {summary.get('analysis_quality', 'N/A')}")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_feature_detection())
