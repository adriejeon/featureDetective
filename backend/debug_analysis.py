#!/usr/bin/env python3
"""
분석 과정 디버깅 스크립트
"""

import asyncio
import json
from services.vertex_ai_analysis_service import VertexAIAnalysisService

async def debug_analysis():
    """실제 크롤링 데이터로 분석 과정 디버깅"""
    print("분석 과정 디버깅 시작...")
    
    # 실제 크롤링된 데이터 (콘솔에서 본 데이터 기반)
    competitor_data = [
        {
            'title': '데이터 모니터링 | groobee',
            'content': '그루비의 데이터 모니터링에 대해 이해합니다. 데이터 모니터링이란? 데이터 모니터링은 온사이…니터링을 할 수 있습니다. 자세한 내용은 데이터 모니터링 조회하기 문서를 확인해 주세요.',
            'description': '',
            'url': 'https://groobee.gitbook.io/groobee-docs/new-admin/undefined-2'
        },
        {
            'title': '구매 확률 세그먼트 만들기 | groobee',
            'content': '그루비 스크립트 설치 이후 방문한 고객의 행동 데이터를 분석합니다. 스크립트 설치 이전 데… 되는 타겟의 수는 캠페인이 노출될 당일 시점을 기준으로 적용되므로 변동될 수 있습니다.',
            'description': '',
            'url': 'https://groobee.gitbook.io/groobee-docs/new-admin/ai/undefined'
        },
        {
            'title': '취향 분석 세그먼트 만들기 | groobee',
            'content': '취향 분석 세그먼트는 그루비에 별도 문의 후 사용할 수 있습니다. 취향 분석 세그먼트는 오…는 사용 가능 기한이 지나면 만료됩니다. 만료된 세그먼트는 캠페인에 사용할 수 없습니다.',
            'description': '',
            'url': 'https://groobee.gitbook.io/groobee-docs/new-admin/ai/undefined-1'
        }
    ]
    
    our_product_data = [
        {
            'title': '자주 묻는 질문 | Genser',
            'content': '여러 개의 검색창에 따로따로 가능한가요? 네, 인스턴스를 여러 개 생성하여 각각의 엔진에 …어떻게 하나요? 기본 사용 구독료 외, 크레딧 기준 사용량에 따라 총 비용이 산정됩니다.',
            'description': '',
            'url': 'https://docs.genser.ai/undefined/faq'
        },
        {
            'title': '젠서 이해하기 | Genser',
            'content': '젠서 시작하기 젠서 이해하기 젠서는 검색, 그 이상의 검색을 만듭니다. gnesr는 어떤 …예: "여름에 신기 좋은 운동화 추천해줘", "사무실에서 입기 좋은 반팔티 뭐가 좋아?"',
            'description': '젠서는 검색, 그 이상의 검색을 만듭니다.',
            'url': 'https://docs.genser.ai/getting-started/learning'
        }
    ]
    
    service = VertexAIAnalysisService()
    
    print(f"Vertex AI 사용 가능: {service.is_available}")
    
    # 경쟁사 데이터 분석
    print("\n=== 경쟁사 데이터 분석 ===")
    print(f"경쟁사 데이터 수: {len(competitor_data)}")
    for i, page in enumerate(competitor_data):
        print(f"  {i+1}. {page['title']}")
        print(f"     내용: {page['content'][:100]}...")
    
    competitor_result = await service._extract_features_from_data(competitor_data, "경쟁사")
    print(f"\n경쟁사 분석 결과:")
    print(f"  추출된 기능 수: {len(competitor_result.get('extracted_features', []))}")
    print(f"  분석 요약: {competitor_result.get('analysis_summary', {})}")
    
    # 우리 제품 데이터 분석
    print("\n=== 우리 제품 데이터 분석 ===")
    print(f"우리 제품 데이터 수: {len(our_product_data)}")
    for i, page in enumerate(our_product_data):
        print(f"  {i+1}. {page['title']}")
        print(f"     내용: {page['content'][:100]}...")
    
    our_product_result = await service._extract_features_from_data(our_product_data, "우리 제품")
    print(f"\n우리 제품 분석 결과:")
    print(f"  추출된 기능 수: {len(our_product_result.get('extracted_features', []))}")
    print(f"  분석 요약: {our_product_result.get('analysis_summary', {})}")
    
    # 전체 분석
    print("\n=== 전체 분석 ===")
    full_result = await service.analyze_features(competitor_data, our_product_data)
    print(f"전체 분석 결과:")
    print(f"  분석 방법: {full_result.get('analysis_method', 'unknown')}")
    print(f"  성공 여부: {full_result.get('success', False)}")
    
    # JSON으로 결과 출력
    print("\n=== 전체 결과 JSON ===")
    print(json.dumps(full_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(debug_analysis())
