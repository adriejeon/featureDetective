#!/usr/bin/env python3
"""
로컬 분석 기능 테스트
"""

import asyncio
from services.vertex_ai_analysis_service import VertexAIAnalysisService

async def test_local_analysis():
    """로컬 분석 기능 테스트"""
    print("로컬 분석 기능 테스트 시작...")
    
    # 테스트 데이터 생성
    competitor_data = [
        {
            'title': '채팅 기능',
            'content': '실시간 채팅 기능을 제공합니다. 메시지 전송과 수신이 가능합니다.',
            'description': '채팅 기능 설명',
            'url': 'https://example.com/chat'
        },
        {
            'title': '파일 업로드',
            'content': '파일을 업로드하고 다운로드할 수 있습니다. 문서 첨부 기능을 제공합니다.',
            'description': '파일 관리 기능',
            'url': 'https://example.com/files'
        },
        {
            'title': '보안 설정',
            'content': '사용자 인증과 권한 관리 기능을 제공합니다. 암호화된 보안 시스템입니다.',
            'description': '보안 기능',
            'url': 'https://example.com/security'
        }
    ]
    
    our_product_data = [
        {
            'title': '검색 기능',
            'content': '강력한 검색 기능을 제공합니다. 필터와 쿼리를 사용하여 원하는 정보를 찾을 수 있습니다.',
            'description': '검색 기능 설명',
            'url': 'https://ourproduct.com/search'
        },
        {
            'title': '분석 리포트',
            'content': '데이터 분석과 통계 리포트를 생성합니다. 인사이트를 제공합니다.',
            'description': '분석 기능',
            'url': 'https://ourproduct.com/analytics'
        }
    ]
    
    service = VertexAIAnalysisService()
    
    try:
        result = await service.analyze_features(competitor_data, our_product_data)
        
        print("\n=== 분석 결과 ===")
        print(f"분석 방법: {result.get('analysis_method', 'unknown')}")
        print(f"성공 여부: {result.get('success', False)}")
        
        # 경쟁사 기능
        competitor_features = result.get('competitor_features', {})
        print(f"\n경쟁사 기능 수: {competitor_features.get('analysis_summary', {}).get('total_features', 0)}")
        for feature in competitor_features.get('extracted_features', []):
            print(f"  - {feature['name']}: {feature['description']}")
        
        # 우리 제품 기능
        our_product_features = result.get('our_product_features', {})
        print(f"\n우리 제품 기능 수: {our_product_features.get('analysis_summary', {}).get('total_features', 0)}")
        for feature in our_product_features.get('extracted_features', []):
            print(f"  - {feature['name']}: {feature['description']}")
        
        # 비교 분석
        comparison = result.get('comparison_analysis', {})
        summary = comparison.get('comparison_summary', {})
        print(f"\n비교 분석:")
        print(f"  공통 기능: {summary.get('common_features', 0)}")
        print(f"  제품1 고유: {summary.get('product1_unique', 0)}")
        print(f"  제품2 고유: {summary.get('product2_unique', 0)}")
        
        print("\n✅ 로컬 분석 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_local_analysis())
