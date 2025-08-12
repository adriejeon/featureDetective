#!/usr/bin/env python3
"""
Vertex AI 클라이언트 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers.vertex_client import VertexAIClient

def test_vertex_ai():
    """Vertex AI 클라이언트 테스트"""
    print("Vertex AI 클라이언트 테스트 시작...")
    
    # 클라이언트 초기화
    client = VertexAIClient()
    
    # 상태 확인
    status = client.get_status()
    print(f"클라이언트 상태: {status}")
    
    if not client.is_available():
        print("❌ Vertex AI 클라이언트를 사용할 수 없습니다.")
        return False
    
    print("✅ Vertex AI 클라이언트 초기화 성공!")
    
    # 간단한 테스트 프롬프트
    test_prompt = "안녕하세요! 간단한 테스트입니다. 'Hello, this is a test'라고 한국어로 응답해주세요."
    
    print(f"테스트 프롬프트 전송: {test_prompt}")
    
    # 콘텐츠 생성
    response = client.generate_content(test_prompt)
    
    if response['success']:
        print("✅ Vertex AI 응답 성공!")
        print(f"응답 내용: {response['content']}")
        print(f"모델: {response['model']}")
        return True
    else:
        print("❌ Vertex AI 응답 실패!")
        print(f"에러: {response['error']}")
        return False

if __name__ == "__main__":
    success = test_vertex_ai()
    if success:
        print("\n🎉 Vertex AI 테스트 성공!")
    else:
        print("\n💥 Vertex AI 테스트 실패!")
        sys.exit(1)

