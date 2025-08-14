#!/usr/bin/env python3
"""
Vertex AI를 사용한 기능 분석 서비스
"""

import json
import asyncio
import os
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

class VertexAIAnalysisService:
    """Vertex AI를 사용한 기능 분석 서비스"""
    
    def __init__(self):
        self.project_id = "groobee-ai"
        self.location = "global"
        self.model = "gemini-2.5-pro"
        
        try:
            # Google Cloud SDK 인증 방식 사용
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
            )
            self.is_available = True
            print("Vertex AI 클라이언트 초기화 성공 (Gemini 2.5 Pro)")
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
            
            # Vertex AI에 분석 요청 (최적화된 버전)
            prompt = f"""다음은 {company_name}의 제품 도움말 문서입니다. 핵심 기능들을 추출해주세요.

=== 문서 내용 ===
{combined_text[:8000]}  # 텍스트 길이 단축

=== 요청 ===
위 문서에서 실제 기능들을 찾아서 JSON 형식으로만 응답하세요:

{{
  "extracted_features": [
    {{
      "name": "기능명",
      "category": "채팅|파일|통화|보안|통합|관리|기타",
      "description": "간단한 설명",
      "confidence": 0.9,
      "source_pages": ["URL"]
    }}
  ],
  "analysis_summary": {{
    "total_features": 0,
    "main_categories": [],
    "document_quality": "high"
  }}
}}

규칙: JSON만 응답, 5-15개 기능 추출, 설명 텍스트 없음"""

            response = await self._generate_content(prompt)
            
            # JSON 파싱 (마크다운에서 JSON 추출)
            try:
                # 먼저 직접 JSON 파싱 시도
                result = json.loads(response)
            except json.JSONDecodeError:
                # 마크다운에서 JSON 부분 추출 시도
                try:
                    import re
                    # ```json ... ``` 패턴 찾기
                    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                    if json_match:
                        json_text = json_match.group(1)
                        result = json.loads(json_text)
                    else:
                        # ``` ... ``` 패턴 찾기 (json 태그 없이)
                        json_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
                        if json_match:
                            json_text = json_match.group(1)
                            # JSON 형식인지 확인
                            if json_text.strip().startswith('{'):
                                result = json.loads(json_text)
                            else:
                                raise Exception("JSON 형식이 아닙니다")
                        else:
                            # {로 시작하는 부분 찾기
                            json_match = re.search(r'\{.*\}', response, re.DOTALL)
                            if json_match:
                                json_text = json_match.group(0)
                                result = json.loads(json_text)
                            else:
                                raise Exception("JSON을 찾을 수 없습니다")
                except Exception as e:
                    print(f"마크다운에서 JSON 추출 실패: {e}")
                    result = {
                        "extracted_features": [],
                        "analysis_summary": {
                            "total_features": 0,
                            "main_categories": [],
                            "document_quality": "low"
                        }
                    }
            
            # 제품 특성 분석 추가
            if result and 'extracted_features' in result:
                product_analysis = await self._analyze_product_characteristics(combined_text, company_name, result)
                result['product_analysis'] = product_analysis
            
            return result
            
        except Exception as e:
            print(f"기능 추출 오류: {e}")
            return {
                'extracted_features': [],
                'analysis_summary': {
                    'total_features': 0,
                    'main_categories': [],
                    'document_quality': 'low'
                }
            }
    
    async def _analyze_product_characteristics(self, combined_text: str, company_name: str, features_result: Dict) -> Dict[str, Any]:
        """제품의 성격과 특징을 분석"""
        try:
            # 추출된 기능 정보를 포함한 분석 프롬프트
            features_text = ""
            if 'extracted_features' in features_result:
                for feature in features_result['extracted_features']:
                    features_text += f"• {feature['name']}: {feature['description']}\n"
            
            prompt = f"""다음은 {company_name}의 제품 도움말 문서와 추출된 기능 목록입니다. 
이 제품의 성격과 특징을 분석해주세요.

=== 도움말 문서 내용 ===
{combined_text[:6000]}

=== 추출된 기능 목록 ===
{features_text}

=== 분석 요청 ===
이 제품의 성격과 특징을 분석하여 JSON 형식으로만 응답하세요:

{{
  "product_characteristics": {{
    "product_type": "제품 유형 (예: 협업 도구, CRM, 마케팅 도구 등)",
    "target_audience": "주요 타겟 사용자",
    "core_value_proposition": "핵심 가치 제안",
    "key_strengths": ["주요 강점 1", "주요 강점 2", "주요 강점 3"],
    "unique_features": ["차별화된 기능 1", "차별화된 기능 2"],
    "business_focus": "비즈니스 집중 영역",
    "technology_stack": "주요 기술 스택 (추정)",
    "market_positioning": "시장 포지셔닝"
  }},
  "feature_analysis": {{
    "most_important_features": ["가장 중요한 기능 1", "가장 중요한 기능 2", "가장 중요한 기능 3"],
    "feature_categories_emphasis": "어떤 카테고리의 기능을 가장 강조하는지",
    "user_experience_focus": "사용자 경험 측면에서의 특징",
    "integration_capabilities": "통합 능력에 대한 특징"
  }}
}}"""

            response = await self._generate_content(prompt)
            
            # JSON 파싱 (마크다운에서 JSON 추출)
            try:
                # 먼저 직접 JSON 파싱 시도
                result = json.loads(response)
            except json.JSONDecodeError:
                # 마크다운에서 JSON 부분 추출 시도
                try:
                    import re
                    # ```json ... ``` 패턴 찾기
                    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                    if json_match:
                        json_text = json_match.group(1)
                        result = json.loads(json_text)
                    else:
                        # ``` ... ``` 패턴 찾기 (json 태그 없이)
                        json_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
                        if json_match:
                            json_text = json_match.group(1)
                            # JSON 형식인지 확인
                            if json_text.strip().startswith('{'):
                                result = json.loads(json_text)
                            else:
                                raise Exception("JSON 형식이 아닙니다")
                        else:
                            # {로 시작하는 부분 찾기
                            json_match = re.search(r'\{.*\}', response, re.DOTALL)
                            if json_match:
                                json_text = json_match.group(0)
                                result = json.loads(json_text)
                            else:
                                raise Exception("JSON을 찾을 수 없습니다")
                except Exception as e:
                    print(f"마크다운에서 JSON 추출 실패: {e}")
                    result = {
                        "product_characteristics": {
                            "product_type": "분석 실패",
                            "target_audience": "분석 실패",
                            "core_value_proposition": "분석 실패",
                            "key_strengths": [],
                            "unique_features": [],
                            "business_focus": "분석 실패",
                            "technology_stack": "분석 실패",
                            "market_positioning": "분석 실패"
                        },
                        "feature_analysis": {
                            "most_important_features": [],
                            "feature_categories_emphasis": "분석 실패",
                            "user_experience_focus": "분석 실패",
                            "integration_capabilities": "분석 실패"
                        }
                    }
            
            return result
            
        except Exception as e:
            print(f"제품 특성 분석 오류: {e}")
            return {
                "product_characteristics": {
                    "product_type": "분석 실패",
                    "target_audience": "분석 실패",
                    "core_value_proposition": "분석 실패",
                    "key_strengths": [],
                    "unique_features": [],
                    "business_focus": "분석 실패",
                    "technology_stack": "분석 실패",
                    "market_positioning": "분석 실패"
                },
                "feature_analysis": {
                    "most_important_features": [],
                    "feature_categories_emphasis": "분석 실패",
                    "user_experience_focus": "분석 실패",
                    "integration_capabilities": "분석 실패"
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
            if not self.is_available:
                return "Vertex AI를 사용할 수 없습니다."
            
            # 제공된 코드 방식으로 Gemini 2.5 Pro 사용
            text1 = types.Part.from_text(text=prompt)
            
            contents = [
                types.Content(
                    role="user",
                    parts=[text1]
                )
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.8,
                max_output_tokens=8192,
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
                ]
            )
            
            response = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                response += chunk.text
            
            return response
            
        except Exception as e:
            print(f"Vertex AI 콘텐츠 생성 오류: {e}")
            return "오류가 발생했습니다."
    
    def _fallback_analysis(self, competitor_data: List[Dict], our_product_data: List[Dict]) -> Dict[str, Any]:
        """Vertex AI를 사용할 수 없을 때의 대체 분석"""
        print("로컬 분석 모드로 기능 추출을 시작합니다...")
        
        # 경쟁사 데이터 분석
        competitor_features = self._extract_features_locally(competitor_data, "경쟁사")
        
        # 우리 제품 데이터 분석
        our_product_features = self._extract_features_locally(our_product_data, "우리 제품")
        
        # 기능 비교 분석
        comparison_analysis = self._compare_features_locally(competitor_features, our_product_features)
        
        return {
            'success': True,
            'competitor_features': competitor_features,
            'our_product_features': our_product_features,
            'comparison_analysis': comparison_analysis,
            'analysis_method': 'local_analysis'
        }
    
    def _extract_features_locally(self, data: List[Dict], company_name: str) -> Dict[str, Any]:
        """로컬에서 키워드 기반으로 기능 추출"""
        try:
            # 모든 텍스트를 결합
            combined_text = ""
            for page in data:
                combined_text += f" {page.get('title', '')} {page.get('content', '')} {page.get('description', '')}"
            
            # 기능 키워드 정의
            feature_keywords = {
                '채팅': ['채팅', '메시지', '대화', '커뮤니케이션', '소통'],
                '파일': ['파일', '업로드', '다운로드', '문서', '첨부'],
                '통화': ['통화', '음성', '화상', '콜', '전화'],
                '보안': ['보안', '암호화', '인증', '권한', '접근'],
                '통합': ['통합', '연동', 'API', '연결', '동기화'],
                '관리': ['관리', '설정', '관리자', '제어', '모니터링'],
                '분석': ['분석', '리포트', '통계', '데이터', '인사이트'],
                '검색': ['검색', '찾기', '필터', '쿼리', '탐색'],
                '알림': ['알림', '알림', '푸시', '이메일', 'SMS'],
                '결제': ['결제', '결제', '구독', '요금', '청구']
            }
            
            extracted_features = []
            found_categories = set()
            
            # 각 카테고리별로 키워드 검색
            for category, keywords in feature_keywords.items():
                found_keywords = []
                for keyword in keywords:
                    if keyword.lower() in combined_text.lower():
                        found_keywords.append(keyword)
                
                if found_keywords:
                    found_categories.add(category)
                    # 페이지에서 해당 키워드가 포함된 내용 찾기
                    relevant_content = ""
                    for page in data:
                        page_text = f"{page.get('title', '')} {page.get('content', '')}"
                        if any(kw.lower() in page_text.lower() for kw in found_keywords):
                            relevant_content += f"{page.get('title', '')}: {page.get('content', '')[:200]}... "
                    
                    extracted_features.append({
                        'name': f"{category} 기능",
                        'category': category,
                        'description': f"{', '.join(found_keywords)} 관련 기능을 제공합니다.",
                        'confidence': 0.7,
                        'source_pages': [page.get('url', '') for page in data if any(kw.lower() in f"{page.get('title', '')} {page.get('content', '')}".lower() for kw in found_keywords)][:3]
                    })
            
            # 제품 특성 분석
            product_analysis = self._analyze_product_characteristics_locally(combined_text, company_name, extracted_features)
            
            return {
                'extracted_features': extracted_features,
                'analysis_summary': {
                    'total_features': len(extracted_features),
                    'main_categories': list(found_categories),
                    'document_quality': 'medium' if len(extracted_features) > 0 else 'low'
                },
                'product_analysis': product_analysis
            }
            
        except Exception as e:
            print(f"로컬 기능 추출 오류: {e}")
            return {
                'extracted_features': [],
                'analysis_summary': {
                    'total_features': 0,
                    'main_categories': [],
                    'document_quality': 'low'
                }
            }
    
    def _analyze_product_characteristics_locally(self, combined_text: str, company_name: str, features: List[Dict]) -> Dict[str, Any]:
        """로컬에서 제품 특성 분석"""
        try:
            # 텍스트에서 제품 유형 추정
            product_type = "웹 서비스"
            if any(word in combined_text.lower() for word in ['앱', '모바일', 'ios', 'android']):
                product_type = "모바일 앱"
            elif any(word in combined_text.lower() for word in ['데스크톱', 'pc', '윈도우', 'mac']):
                product_type = "데스크톱 앱"
            
            # 주요 기능 카테고리 분석
            categories = [f['category'] for f in features]
            main_categories = list(set(categories))
            
            # 타겟 사용자 추정
            target_audience = "일반 사용자"
            if any(word in combined_text.lower() for word in ['기업', '비즈니스', '회사', '조직']):
                target_audience = "기업 사용자"
            elif any(word in combined_text.lower() for word in ['개발자', '프로그래머', '코딩']):
                target_audience = "개발자"
            
            return {
                "product_characteristics": {
                    "product_type": product_type,
                    "target_audience": target_audience,
                    "core_value_proposition": f"{company_name}의 핵심 가치",
                    "key_strengths": [f"{cat} 기능" for cat in main_categories[:3]],
                    "unique_features": [f["name"] for f in features[:2]],
                    "business_focus": "사용자 중심 서비스",
                    "technology_stack": "웹 기반 기술",
                    "market_positioning": "혁신적인 솔루션"
                },
                "feature_analysis": {
                    "most_important_features": [f["name"] for f in features[:3]],
                    "feature_categories_emphasis": f"{', '.join(main_categories[:3])} 기능에 집중",
                    "user_experience_focus": "사용자 친화적 인터페이스",
                    "integration_capabilities": "다양한 플랫폼과의 통합"
                }
            }
            
        except Exception as e:
            print(f"로컬 제품 특성 분석 오류: {e}")
            return {
                "product_characteristics": {
                    "product_type": "분석 실패",
                    "target_audience": "분석 실패",
                    "core_value_proposition": "분석 실패",
                    "key_strengths": [],
                    "unique_features": [],
                    "business_focus": "분석 실패",
                    "technology_stack": "분석 실패",
                    "market_positioning": "분석 실패"
                },
                "feature_analysis": {
                    "most_important_features": [],
                    "feature_categories_emphasis": "분석 실패",
                    "user_experience_focus": "분석 실패",
                    "integration_capabilities": "분석 실패"
                }
            }
    
    def _compare_features_locally(self, competitor_features: Dict, our_product_features: Dict) -> Dict[str, Any]:
        """로컬에서 기능 비교 분석"""
        try:
            competitor_feature_list = competitor_features.get('extracted_features', [])
            our_product_feature_list = our_product_features.get('extracted_features', [])
            
            # 공통 기능 찾기
            competitor_categories = set(f['category'] for f in competitor_feature_list)
            our_categories = set(f['category'] for f in our_product_feature_list)
            common_categories = competitor_categories.intersection(our_categories)
            
            # 각 제품의 고유 기능
            competitor_unique = competitor_categories - our_categories
            our_unique = our_categories - competitor_categories
            
            return {
                'comparison_summary': {
                    'common_features': len(common_categories),
                    'product1_unique': len(competitor_unique),
                    'product2_unique': len(our_unique),
                    'total_features_product1': len(competitor_feature_list),
                    'total_features_product2': len(our_product_feature_list)
                },
                'competitive_analysis': {
                    'product1_advantages': list(competitor_unique),
                    'product2_advantages': list(our_unique),
                    'recommendations': [
                        f"공통 기능: {', '.join(common_categories)}",
                        f"제품1 고유 기능: {', '.join(competitor_unique)}",
                        f"제품2 고유 기능: {', '.join(our_unique)}"
                    ]
                }
            }
            
        except Exception as e:
            print(f"로컬 기능 비교 오류: {e}")
            return {
                'comparison_summary': {
                    'common_features': 0,
                    'product1_unique': 0,
                    'product2_unique': 0,
                    'total_features_product1': 0,
                    'total_features_product2': 0
                },
                'competitive_analysis': {
                    'product1_advantages': [],
                    'product2_advantages': [],
                    'recommendations': []
                }
            }
    
    def _fallback_comparison(self, competitor_features: List, our_product_features: List) -> Dict[str, Any]:
        """기능 비교 실패 시 대체 결과"""
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
                'our_unique_features': 0,
                'competitor_unique_features': 0,
                'overall_assessment': '비교 분석 실패'
            }
        }

# 동기 래퍼 함수
def analyze_features_sync(competitor_data: List[Dict], our_product_data: List[Dict]) -> Dict[str, Any]:
    """동기적으로 기능 분석"""
    return asyncio.run(VertexAIAnalysisService().analyze_features(competitor_data, our_product_data))
