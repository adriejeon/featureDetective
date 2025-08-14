from google import genai
from google.genai import types
import base64

def generate():
    client = genai.Client(
        vertexai=True,
        project="groobee-ai",
        location="us-central1",
    )

    text1 = types.Part.from_text(text="""[Task] 단일 문서 구조화 요약(번역 포함)

[Inputs]
- product: {{제품명}}
- document: {{위 JSON 그대로}}

[Instructions]
1) language 감지: chunks.lang_hint, 내용 감안. 최종 출력은 한국어.
2) 아래 JSON 스키마를 채운 뒤, 마크다운 요약을 간단히 작성.
3) source_refs는 각 항목별로 가장 관련 있는 chunk의 {doc_id, section_id, path, heading}을 포함.
4) 문서에 근거 없는 내용은 "불명확" 또는 []/null.

[JSON schema]
{
 "feature_name": "string|null",
 "purpose": "string|null",
 "user_value": "string|null",
 "entry_points": ["string"],
 "prerequisites": ["string"],
 "permissions_roles": ["string"],
 "key_actions": ["string"],
 "step_by_step": ["string"],
 "ui_elements": ["string"],
 "states_empty_error_loading": ["string"],
 "constraints_limits": ["string"],
 "tips_best_practices": ["string"],
 "examples": ["string"],
 "related_refs": ["string"],        // 문서 내부 교차참조/섹션명
 "terminology_glossary": [{"term":"string","meaning":"string"}],
 "source_refs": [
  {"doc_id":"string","section_id":"string","path":"string","heading":"string"}
 ]
}

[Output format]
1) 위 JSON
2) ---
3) 마크다운 요약(핵심만, 한국어)""")
    
    si_text1 = """당신은 제품 도움말 분석 어시스턴트입니다. 목표:
1) 크롤링된 원문 텍스트에서 기능을 구조화해 요약하고, 영어면 한국어로 번역합니다.
2) UX 관점(탐색→설정→확인/저장→피드백)으로 사용 플로우와 UI 패턴을 추출합니다.
3) 유사 제품과 비교해 차이/격차(Parity Gap)를 도출합니다.

규칙:
- 제공된 입력의 메타데이터(doc_id, section_id, path, title 등)만 근거로 삼고, 없는 정보는 "불명확"으로 표기합니다.
- 최종 출력은 한국어이며, 고유명/명령어/필드명은 원문 병기 허용.
- 내부 사고 과정을 노출하지 마세요(최종 결론만).
- 모든 결과에 source_refs 배열로 근거를 남기되 URL 대신 doc_id/section_id/path를 사용합니다.
- JSON 우선 → 이어서 사람 읽기용 마크다운 요약을 붙입니다."""

    model = "gemini-2.5-pro"
    contents = [
        types.Content(
            role="user",
            parts=[
                text1
            ]
        )
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        seed=0,
        max_output_tokens=32000,
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
            )
        ],
        system_instruction=[types.Part.from_text(text=si_text1)],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
