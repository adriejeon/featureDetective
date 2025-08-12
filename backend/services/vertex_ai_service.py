"""
Vertex AI Gemini를 사용한 의미 분석 서비스
"""

import json
import logging
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
import os

logger = logging.getLogger(__name__)


class VertexAIService:
    """
    Vertex AI Gemini를 사용한 텍스트 분석 서비스
    """
    
    def __init__(self, project_id: str = None, location: str = None):
        """
        Vertex AI 서비스 초기화
        
        Args:
            project_id: Google Cloud 프로젝트 ID (기본값: 환경 변수에서 로드)
            location: Vertex AI 리전 (기본값: 환경 변수에서 로드)
        """
        import os
        
        self.project_id = project_id or os.getenv('VERTEX_AI_PROJECT_ID', 'groobee-ai')
        self.location = location or os.getenv('VERTEX_AI_LOCATION', 'global')
        self.client = None
        self.model = os.getenv('VERTEX_AI_MODEL', 'gemini-2.5-flash-lite')
        
        try:
            self.client = genai.Client(
                vertexai=True,
                project=project_id,
                location=location,
            )
            logger.info(f"Vertex AI 클라이언트 초기화 완료: {project_id}")
        except Exception as e:
            logger.error(f"Vertex AI 클라이언트 초기화 실패: {e}")
            raise
    
    def extract_features_from_text(self, company_name: str, help_text: str) -> Dict[str, Any]:
        """
        도움말 텍스트에서 세부적인 제품 기능을 추출하고 한국어로 번역
        
        Args:
            company_name: 회사명
            help_text: 분석할 도움말 텍스트
            
        Returns:
            추출된 기능 정보 딕셔너리
        """
        try:
            # 프롬프트 템플릿
            prompt_text = f"""다음은 {company_name}의 제품 도움말 문서입니다. 이 텍스트에서 세부적인 제품 기능들을 추출하고 분류해주세요.

=== 도움말 문서 내용 ===
{help_text}

=== 분석 요청 ===
위 문서에서 구체적이고 세부적인 제품 기능을 추출하여 다음 JSON 형식으로 응답해주세요:

{{
  "extracted_features": [
    {{
      "name": "세부 기능명 (예: 챗봇 디자인 커스터마이징, PDF 내보내기, 실시간 알림 설정 등)",
      "category": "UI_UX|보안|통합|성능|관리|분석|커뮤니케이션|파일관리|알림|기타",
      "description": "기능에 대한 상세한 한국어 설명 (영어인 경우 한국어로 번역)",
      "confidence": "추출 신뢰도 (0.0-1.0)",
      "granularity": "기능의 세부 수준 (high/medium/low)"
    }}
  ],
  "analysis_summary": {{
    "total_features": "추출된 기능 수",
    "main_categories": ["주요 카테고리들"],
    "document_quality": "문서 품질 평가 (high/medium/low)",
    "translation_notes": "번역 관련 참고사항"
  }}
}}

추출 기준:
1. 페이지 단위가 아닌 구체적인 기능 단위로 추출
2. 마케팅 문구나 일반적인 설명은 제외
3. 실제 사용자가 활용할 수 있는 세부 기능만 추출
4. 영어 설명은 한국어로 번역
5. 기능의 세부 수준을 고려하여 분류

예시 기능들:
- 챗봇 디자인 커스터마이징
- PDF 내보내기
- 실시간 알림 설정
- 파일 업로드 크기 제한
- 사용자 권한 관리
- API 연동 설정
- 데이터 백업 스케줄링"""

            # 시스템 지시사항
            system_instruction = """당신은 제품 기능 분석 및 번역 전문가입니다.
도움말 문서에서 세부적이고 구체적인 제품 기능을 정확히 추출하고 한국어로 번역하는 것이 전문 분야입니다.

분석 방법:
1. 페이지 단위가 아닌 구체적인 기능 단위로 추출
2. 실제 사용자가 활용할 수 있는 세부 기능만 추출
3. 마케팅 문구나 일반적인 설명은 제외
4. 영어 설명은 자연스러운 한국어로 번역
5. 기능의 세부 수준을 고려하여 분류

추출 기준:
- 구체적이고 측정 가능한 세부 기능
- 사용자가 실제로 설정하거나 사용할 수 있는 기능
- 제품의 핵심 가치를 제공하는 기능
- 기술적으로 구현 가능한 기능
- 기능의 세부 수준을 고려 (high: 매우 세부적, medium: 중간, low: 일반적)

번역 기준:
- 영어 설명을 자연스러운 한국어로 번역
- 기술 용어는 적절한 한국어 용어 사용
- 문맥을 고려한 정확한 번역
- 사용자가 이해하기 쉬운 표현 사용

정확하고 실용적인 분석과 번역을 제공하세요."""

            # 생성 설정
            generate_config = types.GenerateContentConfig(
                temperature=0.3,  # 더 일관된 결과를 위해 낮은 온도
                top_p=0.95,
                max_output_tokens=65535,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
                ],
                system_instruction=[types.Part.from_text(text=system_instruction)],
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )

            # 콘텐츠 생성
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt_text)]
                )
            ]

            # 응답 생성
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_config,
            )

            # JSON 파싱
            response_text = response.text
            logger.info(f"Vertex AI 응답: {response_text[:200]}...")
            
            # JSON 추출 (```json 블록이 있는 경우)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            logger.info(f"기능 추출 완료: {len(result.get('extracted_features', []))}개 기능")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            logger.error(f"응답 텍스트: {response_text}")
            return {
                "extracted_features": [],
                "analysis_summary": {
                    "total_features": 0,
                    "main_categories": [],
                    "document_quality": "low",
                    "error": "JSON 파싱 실패"
                }
            }
        except Exception as e:
            logger.error(f"기능 추출 중 오류: {e}")
            return {
                "extracted_features": [],
                "analysis_summary": {
                    "total_features": 0,
                    "main_categories": [],
                    "document_quality": "low",
                    "error": str(e)
                }
            }
    
    def compare_products(self, product1_name: str, product1_features: List[Dict], 
                        product2_name: str, product2_features: List[Dict]) -> Dict[str, Any]:
        """
        두 제품의 기능을 비교 분석
        
        Args:
            product1_name: 첫 번째 제품명
            product1_features: 첫 번째 제품의 기능 리스트
            product2_name: 두 번째 제품명
            product2_features: 두 번째 제품의 기능 리스트
            
        Returns:
            비교 분석 결과
        """
        try:
            # 기능 리스트를 JSON 문자열로 변환
            features1_json = json.dumps(product1_features, ensure_ascii=False, indent=2)
            features2_json = json.dumps(product2_features, ensure_ascii=False, indent=2)
            
            prompt_text = f"""다음은 두 제품의 기능 비교 분석 요청입니다.

=== {product1_name}의 기능 ===
{features1_json}

=== {product2_name}의 기능 ===
{features2_json}

=== 비교 분석 요청 ===
두 제품의 기능을 비교하여 다음 JSON 형식으로 분석 결과를 제공해주세요:

{{
  "comparison_summary": {{
    "total_features_product1": "첫 번째 제품의 총 기능 수",
    "total_features_product2": "두 번째 제품의 총 기능 수",
    "common_features": "공통 기능 수",
    "unique_features_product1": "첫 번째 제품만의 고유 기능 수",
    "unique_features_product2": "두 번째 제품만의 고유 기능 수"
  }},
  "feature_comparison": [
    {{
      "feature_name": "기능명",
      "product1_support": "첫 번째 제품 지원 여부 (true/false)",
      "product2_support": "두 번째 제품 지원 여부 (true/false)",
      "comparison_type": "common|unique_product1|unique_product2",
      "significance": "기능의 중요도 (high/medium/low)"
    }}
  ],
  "competitive_analysis": {{
    "product1_advantages": ["첫 번째 제품의 장점들"],
    "product2_advantages": ["두 번째 제품의 장점들"],
    "market_positioning": "시장 포지셔닝 분석",
    "recommendations": ["개선 권장사항들"]
  }}
}}"""

            # 시스템 지시사항
            system_instruction = """당신은 경쟁사 분석 전문가입니다.
두 제품의 기능을 비교하여 경쟁 우위와 갭을 분석하는 것이 전문 분야입니다.

분석 방법:
1. 서로 다른 표현이지만 동일한 기능인지 의미론적으로 판단
2. 각 제품의 고유 기능과 공통 기능을 구분
3. 기능 격차를 객관적으로 평가
4. UX 리서치 관점에서 실용적인 인사이트 제공

비교 기준:
- 기능의 본질적 목적과 사용자 가치로 판단
- 단순 키워드 매칭이 아닌 의미 기반 비교
- 사용자 경험 관점에서 기능의 중요도 고려
- 시장 표준 대비 혁신성 평가

객관적이고 균형잡힌 분석을 제공하세요."""

            # 생성 설정
            generate_config = types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.95,
                max_output_tokens=65535,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
                ],
                system_instruction=[types.Part.from_text(text=system_instruction)],
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )

            # 콘텐츠 생성
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt_text)]
                )
            ]

            # 응답 생성
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_config,
            )

            # JSON 파싱
            response_text = response.text
            logger.info(f"제품 비교 분석 완료")
            
            # JSON 추출
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"제품 비교 JSON 파싱 오류: {e}")
            return {
                "comparison_summary": {},
                "feature_comparison": [],
                "competitive_analysis": {
                    "error": "JSON 파싱 실패"
                }
            }
        except Exception as e:
            logger.error(f"제품 비교 분석 중 오류: {e}")
            return {
                "comparison_summary": {},
                "feature_comparison": [],
                "competitive_analysis": {
                    "error": str(e)
                }
            }
    
    def analyze_keyword_support(self, keyword: str, help_text: str) -> Dict[str, Any]:
        """
        특정 키워드의 지원 여부를 AI로 분석
        
        Args:
            keyword: 분석할 키워드
            help_text: 도움말 텍스트
            
        Returns:
            키워드 지원 분석 결과
        """
        try:
            prompt_text = f"""다음 키워드가 도움말 문서에서 지원되는지 분석해주세요.

=== 분석할 키워드 ===
{keyword}

=== 도움말 문서 내용 ===
{help_text}

=== 분석 요청 ===
위 키워드의 지원 여부를 다음 JSON 형식으로 분석해주세요:

{{
  "keyword": "{keyword}",
  "support_status": "O|X|△",
  "confidence_score": "신뢰도 점수 (0.0-1.0)",
  "matched_text": "매칭된 텍스트 내용",
  "analysis_reason": "지원 여부 판단 근거",
  "related_features": ["관련된 기능들"],
  "limitations": ["제한사항이나 조건들"]
}}

분석 기준:
- O: 명확하게 지원됨
- X: 명확하게 지원되지 않음
- △: 부분적으로 지원되거나 조건부 지원"""

            # 시스템 지시사항
            system_instruction = """당신은 제품 기능 분석 전문가입니다.
도움말 문서에서 특정 기능의 지원 여부를 정확히 판단하는 것이 전문 분야입니다.

분석 방법:
1. 키워드와 직접적으로 관련된 내용을 찾기
2. 유사한 표현이나 동의어도 고려
3. 부정적인 표현이나 제한사항 확인
4. 맥락을 고려한 종합적 판단

판단 기준:
- 명시적 언급이 있는 경우
- 유사한 기능이나 대안이 있는 경우
- 제한사항이나 조건이 있는 경우
- 전혀 언급되지 않는 경우

정확하고 객관적인 분석을 제공하세요."""

            # 생성 설정
            generate_config = types.GenerateContentConfig(
                temperature=0.2,
                top_p=0.95,
                max_output_tokens=2048,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
                ],
                system_instruction=[types.Part.from_text(text=system_instruction)],
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )

            # 콘텐츠 생성
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt_text)]
                )
            ]

            # 응답 생성
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_config,
            )

            # JSON 파싱
            response_text = response.text
            logger.info(f"키워드 분석 완료: {keyword}")
            
            # JSON 추출
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"키워드 분석 JSON 파싱 오류: {e}")
            return {
                "keyword": keyword,
                "support_status": "X",
                "confidence_score": 0.0,
                "matched_text": "",
                "analysis_reason": "JSON 파싱 실패",
                "related_features": [],
                "limitations": []
            }
        except Exception as e:
            logger.error(f"키워드 분석 중 오류: {e}")
            return {
                "keyword": keyword,
                "support_status": "X",
                "confidence_score": 0.0,
                "matched_text": "",
                "analysis_reason": str(e),
                "related_features": [],
                "limitations": []
            }
