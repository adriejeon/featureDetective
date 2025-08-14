#!/usr/bin/env python3
"""
기능 감지 서비스 전체 플로우 테스트
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.feature_detection_service import FeatureDetectionService

async def test_feature_detection():
    """기능 감지 전체 플로우 테스트"""
    try:
        print("기능 감지 서비스 초기화...")
        service = FeatureDetectionService()
        
        # 테스트 URL들 (실제 존재하는 도움말 페이지들)
        competitor_urls = [
            "https://slack.com/help/articles/115004071768-What-is-Slack-",
            "https://support.discord.com/hc/en-us/articles/360045138571-Getting-Started"
        ]
        
        our_product_urls = [
            "https://slack.com/help/articles/115004071768-What-is-Slack-"
        ]
        
        print("기능 감지 시작...")
        result = await service.detect_features_from_urls(
            competitor_urls, 
            our_product_urls, 
            "테스트 프로젝트"
        )
        
        print(f"결과: {result}")
        
        if 'analysis_results' in result:
            product_features = result['analysis_results']['product_features']
            product_mapping = result['analysis_results']['product_feature_mapping']
            
            print("\n=== 제품별 기능 분석 결과 ===")
            for product_name, features in product_features.items():
                print(f"\n{product_name}:")
                extracted_features = features.get('extracted_features', [])
                print(f"  추출된 기능 수: {len(extracted_features)}")
                for i, feature in enumerate(extracted_features[:5], 1):  # 처음 5개만 표시
                    print(f"    {i}. {feature.get('name', 'N/A')}")
            
            print("\n=== 제품별 기능 매핑 결과 ===")
            for product_name, feature_mapping in product_mapping.items():
                print(f"\n{product_name}:")
                for feature_name, mapping_info in list(feature_mapping.items())[:5]:  # 처음 5개만 표시
                    status = mapping_info.get('status', 'N/A')
                    description = mapping_info.get('description', 'N/A')
                    print(f"  {feature_name}: {status} - {description[:50]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_feature_detection())
