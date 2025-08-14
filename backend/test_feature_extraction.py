#!/usr/bin/env python3
"""
Vertex AI 기능 추출 테스트
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vertex_ai_service import VertexAIService

def test_feature_extraction():
    """기능 추출 테스트"""
    try:
        print("Vertex AI 서비스 초기화...")
        vertex_ai = VertexAIService()
        
        # 테스트 텍스트
        test_text = """
        Slack은 팀 협업을 위한 메시징 플랫폼입니다.
        
        주요 기능:
        - 실시간 채팅: 팀원들과 실시간으로 대화할 수 있습니다
        - 파일 공유: 문서, 이미지, 비디오를 쉽게 공유할 수 있습니다
        - 화상 회의: 비디오 통화로 원격 회의를 진행할 수 있습니다
        - 봇 연동: 다양한 서비스와 봇을 연동할 수 있습니다
        - 모바일 앱: 스마트폰에서도 사용할 수 있습니다
        - API 제공: 개발자가 자체 앱을 연동할 수 있습니다
        - 보안 설정: 엔터프라이즈급 보안 기능을 제공합니다
        - 알림 설정: 중요한 메시지를 놓치지 않도록 알림을 설정할 수 있습니다
        """
        
        print("기능 추출 시작...")
        result = vertex_ai.extract_features_from_text("Slack", test_text, "https://slack.com")
        
        print(f"추출 결과: {result}")
        
        if 'extracted_features' in result and result['extracted_features']:
            print(f"✅ {len(result['extracted_features'])}개 기능 추출 성공!")
            for i, feature in enumerate(result['extracted_features'], 1):
                print(f"  {i}. {feature.get('name', 'N/A')} - {feature.get('description', 'N/A')}")
        else:
            print("❌ 기능 추출 실패 또는 빈 결과")
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_feature_extraction()

