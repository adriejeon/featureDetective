#!/usr/bin/env python3
"""
Vertex AI 응답 확인 테스트
"""

import os
import sys
import asyncio
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vertex_ai_analysis_service import VertexAIAnalysisService
from services.crawlee_crawler_service import RecursiveCrawlerService

async def test_vertex_ai_response():
    """Vertex AI 응답 확인 테스트"""
    try:
        print("Vertex AI 응답 확인 테스트 시작...")
        
        # 서비스 초기화
        vertex_ai_service = VertexAIAnalysisService()
        crawler_service = RecursiveCrawlerService()
        
        # 테스트 URL
        test_url = "https://slack.com/help/articles/115004071768-What-is-Slack-"
        
        print(f"크롤링 시작: {test_url}")
        data = await crawler_service.crawl_website(test_url)
        print(f"크롤링 완료: {len(data)}개 페이지")
        
        # 크롤링된 데이터 확인
        print("\n=== 크롤링된 데이터 샘플 ===")
        for i, page in enumerate(data[:2]):  # 처음 2개만
            print(f"\n--- 페이지 {i+1} ---")
            print(f"제목: {page.get('title', 'N/A')}")
            print(f"URL: {page.get('url', 'N/A')}")
            print(f"내용 길이: {len(page.get('content', ''))}자")
            print(f"내용 샘플: {page.get('content', '')[:200]}...")
        
        # Vertex AI에 직접 요청
        print("\n=== Vertex AI 직접 요청 ===")
        
        # 모든 페이지의 텍스트를 결합
        combined_text = ""
        for page in data:
            combined_text += f"\n=== 페이지: {page.get('title', '제목 없음')} ===\n"
            combined_text += f"URL: {page.get('url', '')}\n"
            combined_text += f"내용: {page.get('content', '')}\n"
            combined_text += f"설명: {page.get('description', '')}\n"
        
        # 간단한 프롬프트로 테스트
        simple_prompt = f"""다음은 Slack의 도움말 문서입니다. 이 텍스트에서 실제 기능들을 찾아주세요.

=== 문서 내용 ===
{combined_text[:5000]}

위 문서에서 Slack의 실제 기능들을 찾아서 JSON 형식으로 응답해주세요:

{{
  "features": [
    {{
      "name": "기능명",
      "description": "기능 설명"
    }}
  ]
}}

실제 사용 가능한 기능만 찾아주세요."""

        print("Vertex AI 요청 중...")
        response = await vertex_ai_service._generate_content(simple_prompt)
        print("Vertex AI 응답 받음")
        
        print("\n=== Vertex AI 응답 ===")
        print(response)
        
        # JSON 파싱 시도
        try:
            parsed = json.loads(response)
            print("\n=== 파싱된 JSON ===")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
        except json.JSONDecodeError as e:
            print(f"\nJSON 파싱 실패: {e}")
            print("응답이 JSON 형식이 아닙니다.")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vertex_ai_response())

