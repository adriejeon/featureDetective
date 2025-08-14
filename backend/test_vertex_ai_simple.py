#!/usr/bin/env python3
"""
Vertex AI 연결 테스트
"""

import asyncio
from services.vertex_ai_analysis_service import VertexAIAnalysisService

async def test_vertex_ai_connection():
    """Vertex AI 연결 테스트"""
    print("Vertex AI 연결 테스트 시작...")
    
    service = VertexAIAnalysisService()
    print(f"Vertex AI 사용 가능: {service.is_available}")
    
    if not service.is_available:
        print("Vertex AI를 사용할 수 없습니다. Google Cloud 인증을 확인하세요.")
        return
    
    # 간단한 테스트 프롬프트
    test_prompt = "안녕하세요. 간단한 테스트입니다. '테스트 성공'이라고만 응답해주세요."
    
    try:
        response = await service._generate_content(test_prompt)
        print(f"Vertex AI 응답: {response}")
    except Exception as e:
        print(f"Vertex AI 테스트 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_vertex_ai_connection())
