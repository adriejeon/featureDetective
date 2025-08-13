#!/usr/bin/env python3
"""
Vertex AI를 사용한 기능 분석 서비스
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

class VertexAIAnalysisService:
    """Vertex AI를 사용한 기능 분석 서비스"""
    
    def __init__(self):
        self.project_id = "groobee-ai"
        self.location = "global"
        self.model = "gemini-2.5-flash-lite"
        
        try:
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
            )
            self.is_available = True
            print("Vertex AI 클라이언트 초기화 성공")
        except Exception as e:
            print(f"Vertex AI 클라이언트 초기화 실패: {e}")
            self.is_available = False
    
    async def analyze_features(self, competitor_data: List[Dict], our_product_data: List[Dict]) -> Dict[str, Any]:
        """크롤링된 데이터를 분석하여 기능을 분류하고 비교"""
        if not self.is_available:
            return self._fallback_analysis(competitor_data, our_product_data)
        
        try:
            # 경쟁사 데이터 분석
            competitor_features = await self._extract_features_from_data(competitor_data, "경쟁사")
            
            # 우리 제품 데이터 분석
            our_product_features = await self._extract_features_from_data(our_product_data, "우리 제품")
            
            # 기능 비교 분석
            comparison_analysis = await self._compare_features(competitor_features, our_product_features)
            
            return {
                'success': True,
                'competitor_features': competitor_features,
                'our_product_features': our_product_features,
                'comparison_analysis': comparison_analysis,
                'analysis_method': 'vertex_ai'
            }
            
        except Exception as e:
            print(f"Vertex AI 분석 오류: {e}")
            return self._fallback_analysis(competitor_data, our_product_data)
    
    async def _extract_features_from_data(self, data: List[Dict], company_name: str) -> Dict[str, Any]:
        """크롤링된 데이터에서 기능 추출"""
        try:
            # 모든 페이지의 텍스트를 결합
            combined_text = ""
            for page in data:
                combined_text += f"\n=== 페이지: {page.get('title', '제목 없음')} ===\n"
                combined_text += f"URL: {page.get('url', '')}\n"
                combined_text += f"내용: {page.get('content', '')}\n"
                combined_text += f"설명: {page.get('description', '')}\n"
                
                # 링크 정보도 추가
                links = page.get('links', [])
                if links:
                    combined_text += f"링크: {', '.join([link.get('text', '') for link in links[:10]])}\n"
            
            # Vertex AI에 분석 요청
            prompt = f"""다음은 {company_name}의 제품 도움말 문서입니다. 이 텍스트에서 제품의 핵심 기능들을 추출하고 분류해주세요.

=== 도움말 문서 내용 ===
{combined_text[:8000]}  # 텍스트 길이 제한

=== 분석 요청 ===
위 문서에서 제품 기능을 추출하여 다음 JSON 형식으로 응답해주세요:

{{
  "extracted_features": [
    {{
      "name": "기능명",
      "category": "UI_UX|보안|통합|성능|관리|기타",
      "description": "기능에 대한 간단한 설명",
      "confidence": "추출 신뢰도 (0.0-1.0)",
      "source_pages": ["출처 페이지 URL들"]
    }}
  ],
  "analysis_summary": {{
    "total_features": "추출된 기능 수",
    "main_categories": ["주요 카테고리들"],
    "document_quality": "문서 품질 평가 (high/medium/low)"
  }}
}}

마케팅 문구나 일반적인 설명은 제외하고, 구체적으로 사용 가능한 기능만 추출해주세요."""

            response = await self._generate_content(prompt)
            
            # JSON 파싱
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 구조 반환
                return {
                    "extracted_features": [],
                    "analysis_summary": {
                        "total_features": 0,
                        "main_categories": [],
                        "document_quality": "low"
                    }
                }
                
        except Exception as e:
            print(f"기능 추출 오류: {e}")
            return {
                "extracted_features": [],
                "analysis_summary": {
                    "total_features": 0,
                    "main_categories": [],
                    "document_quality": "low"
                }
            }
    
    async def _compare_features(self, competitor_features: Dict, our_product_features: Dict) -> Dict[str, Any]:
        """두 제품의 기능을 비교 분석"""
        try:
            competitor_feature_list = competitor_features.get('extracted_features', [])
            our_product_feature_list = our_product_features.get('extracted_features', [])
            
            prompt = f"""당신은 경쟁사 분석 전문가입니다.
두 제품의 기능을 비교하여 경쟁 우위와 갭을 분석하는 것이 전문 분야입니다.

=== 경쟁사 기능 ===
{json.dumps(competitor_feature_list, ensure_ascii=False, indent=2)}

=== 우리 제품 기능 ===
{json.dumps(our_product_feature_list, ensure_ascii=False, indent=2)}

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

다음 JSON 형식으로 응답해주세요:

{{
  "feature_comparison": [
    {{
      "feature_name": "기능명",
      "competitor_implementation": "경쟁사에서의 구현 방식",
      "our_implementation": "우리 제품에서의 구현 방식",
      "advantage": "우리 제품의 장점",
      "gap": "개선이 필요한 부분",
      "priority": "우선순위 (high/medium/low)"
    }}
  ],
  "competitive_analysis": {{
    "our_advantages": ["우리 제품의 강점들"],
    "competitor_advantages": ["경쟁사의 강점들"],
    "market_gaps": ["시장에서 부족한 기능들"],
    "recommendations": ["개선 제안사항들"]
  }},
  "summary": {{
    "total_comparable_features": "비교 가능한 기능 수",
    "our_unique_features": "우리만의 고유 기능 수",
    "competitor_unique_features": "경쟁사만의 고유 기능 수",
    "overall_assessment": "전체적인 경쟁력 평가"
  }}
}}

객관적이고 균형잡힌 분석을 제공하세요."""

            response = await self._generate_content(prompt)
            
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                return self._fallback_comparison(competitor_feature_list, our_product_feature_list)
                
        except Exception as e:
            print(f"기능 비교 오류: {e}")
            return self._fallback_comparison(
                competitor_features.get('extracted_features', []),
                our_product_features.get('extracted_features', [])
            )
    
    async def _generate_content(self, prompt: str) -> str:
        """Vertex AI에 콘텐츠 생성 요청"""
        try:
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

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]

            generate_content_config = types.GenerateContentConfig(
                temperature=0.7,
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

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            
            return response.text
            
        except Exception as e:
            print(f"Vertex AI 콘텐츠 생성 오류: {e}")
            raise e
    
    def _fallback_analysis(self, competitor_data: List[Dict], our_product_data: List[Dict]) -> Dict[str, Any]:
        """Vertex AI가 사용 불가능할 때의 기본 분석"""
        return {
            'success': False,
            'competitor_features': {
                'extracted_features': [],
                'analysis_summary': {
                    'total_features': 0,
                    'main_categories': [],
                    'document_quality': 'low'
                }
            },
            'our_product_features': {
                'extracted_features': [],
                'analysis_summary': {
                    'total_features': 0,
                    'main_categories': [],
                    'document_quality': 'low'
                }
            },
            'comparison_analysis': {
                'feature_comparison': [],
                'competitive_analysis': {
                    'our_advantages': [],
                    'competitor_advantages': [],
                    'market_gaps': [],
                    'recommendations': []
                },
                'summary': {
                    'total_comparable_features': 0,
                    'our_unique_features': 0,
                    'competitor_unique_features': 0,
                    'overall_assessment': '분석 불가'
                }
            },
            'analysis_method': 'fallback',
            'error': 'Vertex AI 서비스를 사용할 수 없습니다.'
        }
    
    def _fallback_comparison(self, competitor_features: List[Dict], our_product_features: List[Dict]) -> Dict[str, Any]:
        """기본 기능 비교 분석"""
        return {
            'feature_comparison': [],
            'competitive_analysis': {
                'our_advantages': [],
                'competitor_advantages': [],
                'market_gaps': [],
                'recommendations': []
            },
            'summary': {
                'total_comparable_features': 0,
                'our_unique_features': len(our_product_features),
                'competitor_unique_features': len(competitor_features),
                'overall_assessment': '기본 분석 완료'
            }
        }

# 동기 래퍼 함수
def analyze_features_sync(competitor_data: List[Dict], our_product_data: List[Dict]) -> Dict[str, Any]:
    """동기적으로 기능 분석"""
    return asyncio.run(VertexAIAnalysisService().analyze_features(competitor_data, our_product_data))
