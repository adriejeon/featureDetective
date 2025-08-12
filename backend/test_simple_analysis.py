#!/usr/bin/env python3
"""
간단한 Vertex AI 분석 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers.vertex_client import VertexAIClient

def test_simple_analysis():
    """간단한 Vertex AI 분석 테스트"""
    print("간단한 Vertex AI 분석 테스트 시작...")
    
    try:
        # Vertex AI 클라이언트 초기화
        client = VertexAIClient()
        print("✅ Vertex AI 클라이언트 초기화 성공!")
        
        # 간단한 분석 프롬프트
        prompt = """
다음은 두 제품의 도움말 사이트 정보입니다. 각 제품의 주요 기능을 추출하고 비교해주세요.

**제품 A (Gelatto)**: AI 챗봇 플랫폼
- 대시보드 기능
- 지식 센터
- 젤라또 만들기
- 기본 설정
- 지식 구조 관리

**제품 B (Example)**: 일반적인 웹사이트
- 기본 웹페이지 기능

위 정보를 바탕으로 다음 JSON 형식으로 응답해주세요:

{
  "extracted_features": [
    {
      "name": "기능명",
      "category": "UI_UX|보안|통합|성능|관리|기타",
      "description": "기능에 대한 간단한 설명",
      "product": "A|B",
      "confidence": 0.9
    }
  ],
  "comparison": {
    "product_a_features": 5,
    "product_b_features": 1,
    "unique_to_a": ["대시보드", "지식 센터"],
    "unique_to_b": [],
    "common_features": []
  }
}
"""
        
        print("Vertex AI 분석 요청 중...")
        response = client.generate_content(prompt)
        
        if response['success']:
            print("✅ Vertex AI 분석 성공!")
            print(f"응답 길이: {len(response['content'])}자")
            print("\n응답 내용:")
            print(response['content'][:500] + "..." if len(response['content']) > 500 else response['content'])
            
            # JSON 파싱 시도
            try:
                json_result = client.extract_json_from_response(response['content'])
                print(f"\nJSON 파싱 성공: {len(json_result.get('extracted_features', []))}개 기능 발견")
            except:
                print("\nJSON 파싱 실패")
        else:
            print(f"❌ Vertex AI 분석 실패: {response['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_analysis()
    if success:
        print("\n🎉 간단한 분석 테스트 성공!")
    else:
        print("\n💥 간단한 분석 테스트 실패!")
        sys.exit(1)
