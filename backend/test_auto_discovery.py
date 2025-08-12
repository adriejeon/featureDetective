#!/usr/bin/env python3
"""
자동 분석 서비스 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auto_feature_discovery_service import AutoFeatureDiscoveryService

def test_auto_discovery():
    """자동 분석 서비스 테스트"""
    print("자동 분석 서비스 테스트 시작...")
    
    try:
        # 서비스 초기화
        service = AutoFeatureDiscoveryService()
        print("✅ 자동 분석 서비스 초기화 성공!")
        
        # 모듈 상태 확인
        print(f"크롤러 초기화: {service.help_crawler is not None}")
        print(f"Vertex AI 클라이언트 초기화: {service.vertex_client is not None}")
        print(f"기능 추출기 초기화: {service.feature_extractor is not None}")
        print(f"기능 비교기 초기화: {service.feature_comparator is not None}")
        
        # 간단한 테스트 URL
        competitor_url = "https://docs.gelatto.ai/"
        our_product_url = "https://example.com"
        
        print(f"\n테스트 URL:")
        print(f"경쟁사: {competitor_url}")
        print(f"우리 제품: {our_product_url}")
        
        # 자동 분석 실행
        print("\n자동 분석 실행 중...")
        result = service.discover_and_compare_features_with_links(competitor_url, our_product_url)
        
        print(f"\n분석 결과:")
        print(f"성공: {result.get('success', False)}")
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"분석 방법: {data.get('analysis_method', 'N/A')}")
            print(f"경쟁사 기능 수: {data.get('competitor_features_count', 0)}")
            print(f"우리 제품 기능 수: {data.get('our_product_features_count', 0)}")
            print(f"발견된 기능 수: {data.get('discovered_features', 0)}")
            
            if data.get('results'):
                print(f"결과 수: {len(data['results'])}")
                for i, feature in enumerate(data['results'][:3]):
                    print(f"  {i+1}. {feature.get('title', 'N/A')}")
        else:
            print(f"에러: {result.get('error', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 자동 분석 서비스 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auto_discovery()
    if success:
        print("\n🎉 자동 분석 서비스 테스트 성공!")
    else:
        print("\n💥 자동 분석 서비스 테스트 실패!")
        sys.exit(1)

