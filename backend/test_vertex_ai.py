#!/usr/bin/env python3
"""
Vertex AI 클라이언트 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google import genai
from google.genai import types
import json

def test_vertex_ai():
    """Vertex AI 연동 테스트"""
    try:
        client = genai.Client(
            vertexai=True,
            project="groobee-ai",
            location="global",
        )
        
        # 간단한 테스트 프롬프트
        test_prompt = "안녕하세요! Vertex AI가 정상적으로 작동하는지 테스트해주세요. 한국어로 답변해주세요."
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=test_prompt)]
            )
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1000,
        )
        
        print("Vertex AI 테스트 시작...")
        print("프롬프트:", test_prompt)
        print("\n응답:")
        
        # 스트리밍 응답 처리
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-pro",
            contents=contents,
            config=generate_content_config,
        ):
            if hasattr(chunk, 'text') and chunk.text:
                response_text += chunk.text
                print(chunk.text, end="", flush=True)
        
        if response_text:
            print(f"\n\n✅ Vertex AI 연동 성공! 응답 길이: {len(response_text)} 문자")
        else:
            print("\n\n⚠️ 응답이 비어있습니다. 모델 설정을 확인해주세요.")
        
    except Exception as e:
        print(f"❌ Vertex AI 연동 실패: {e}")
        print("인증 상태를 확인해주세요.")

if __name__ == "__main__":
    test_vertex_ai()

