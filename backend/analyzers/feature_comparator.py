"""
기능 비교기
두 제품의 기능을 비교하여 경쟁 분석 수행
"""

import json
import logging
from typing import Dict, List, Any, Optional
from .vertex_client import VertexAIClient

logger = logging.getLogger(__name__)


class FeatureComparator:
    """기능 비교기"""
    
    def __init__(self, vertex_client: VertexAIClient = None):
        """
        기능 비교기 초기화
        
        Args:
            vertex_client: Vertex AI 클라이언트
        """
        self.vertex_client = vertex_client or VertexAIClient()
        
        # 시스템 지시사항
        self.system_instruction = """당신은 경쟁사 분석 전문가입니다.
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
        if not self.vertex_client.is_available():
            return {
                'success': False,
                'error': 'Vertex AI 서비스를 사용할 수 없습니다.',
                'comparison_summary': {},
                'feature_comparison': [],
                'competitive_analysis': {}
            }
        
        try:
            # 프롬프트 생성
            prompt = self._create_comparison_prompt(product1_name, product1_features, 
                                                  product2_name, product2_features)
            
            # Vertex AI로 제품 비교
            response = self.vertex_client.generate_content(
                prompt=prompt,
                system_instruction=self.system_instruction,
                config={'temperature': 0.3}
            )
            
            if not response['success']:
                return {
                    'success': False,
                    'error': response['error'],
                    'comparison_summary': {},
                    'feature_comparison': [],
                    'competitive_analysis': {}
                }
            
            # JSON 파싱
            result = self.vertex_client.extract_json_from_response(response['content'])
            
            if 'error' in result:
                return {
                    'success': False,
                    'error': result['error'],
                    'comparison_summary': {},
                    'feature_comparison': [],
                    'competitive_analysis': {}
                }
            
            # 결과 검증 및 정리
            validated_result = self._validate_and_clean_comparison(result)
            
            logger.info(f"제품 비교 분석 완료: {len(validated_result.get('feature_comparison', []))}개 기능 비교")
            
            return {
                'success': True,
                'comparison_summary': validated_result.get('comparison_summary', {}),
                'feature_comparison': validated_result.get('feature_comparison', []),
                'competitive_analysis': validated_result.get('competitive_analysis', {}),
                'raw_response': response['content'][:500] + '...' if len(response['content']) > 500 else response['content']
            }
            
        except Exception as e:
            error_msg = f"제품 비교 분석 중 오류: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'comparison_summary': {},
                'feature_comparison': [],
                'competitive_analysis': {}
            }
    
    def _create_comparison_prompt(self, product1_name: str, product1_features: List[Dict],
                                product2_name: str, product2_features: List[Dict]) -> str:
        """기능 비교를 위한 프롬프트 생성"""
        # 기능 리스트를 JSON 문자열로 변환
        features1_json = json.dumps(product1_features, ensure_ascii=False, indent=2)
        features2_json = json.dumps(product2_features, ensure_ascii=False, indent=2)
        
        return f"""다음은 두 제품의 기능 비교 분석 요청입니다.

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
      "significance": "기능의 중요도 (high/medium/low)",
      "similarity_score": "기능 유사도 점수 (0.0-1.0)"
    }}
  ],
  "competitive_analysis": {{
    "product1_advantages": ["첫 번째 제품의 장점들"],
    "product2_advantages": ["두 번째 제품의 장점들"],
    "market_positioning": "시장 포지셔닝 분석",
    "recommendations": ["개선 권장사항들"],
    "feature_gaps": ["기능 격차 분석"]
  }}
}}

비교 기준:
1. 서로 다른 표현이지만 동일한 기능인지 의미론적으로 판단
2. 각 제품의 고유 기능과 공통 기능을 구분
3. 기능 격차를 객관적으로 평가
4. 사용자 경험 관점에서 기능의 중요도 고려"""
    
    def _validate_and_clean_comparison(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """비교 결과 검증 및 정리"""
        try:
            comparison_summary = result.get('comparison_summary', {})
            feature_comparison = result.get('feature_comparison', [])
            competitive_analysis = result.get('competitive_analysis', {})
            
            # 기능 비교 검증 및 정리
            validated_comparisons = []
            for comparison in feature_comparison:
                if self._is_valid_comparison(comparison):
                    cleaned_comparison = self._clean_comparison(comparison)
                    validated_comparisons.append(cleaned_comparison)
            
            # 비교 요약 업데이트
            comparison_summary['total_comparisons'] = len(validated_comparisons)
            
            return {
                'comparison_summary': comparison_summary,
                'feature_comparison': validated_comparisons,
                'competitive_analysis': competitive_analysis
            }
            
        except Exception as e:
            logger.error(f"비교 결과 검증 중 오류: {e}")
            return result
    
    def _is_valid_comparison(self, comparison: Dict[str, Any]) -> bool:
        """비교 결과 유효성 검사"""
        required_fields = ['feature_name', 'product1_support', 'product2_support', 'comparison_type']
        
        # 필수 필드 확인
        for field in required_fields:
            if field not in comparison:
                return False
        
        # 기능명 확인
        if not comparison['feature_name'] or len(comparison['feature_name']) < 2:
            return False
        
        # 지원 여부 확인
        if not isinstance(comparison['product1_support'], bool) or not isinstance(comparison['product2_support'], bool):
            return False
        
        # 비교 타입 확인
        valid_types = ['common', 'unique_product1', 'unique_product2']
        if comparison['comparison_type'] not in valid_types:
            comparison['comparison_type'] = 'common'
        
        # 중요도 확인
        significance = comparison.get('significance', 'medium')
        valid_significance = ['high', 'medium', 'low']
        if significance not in valid_significance:
            comparison['significance'] = 'medium'
        
        # 유사도 점수 확인
        similarity_score = comparison.get('similarity_score', 0.5)
        if not isinstance(similarity_score, (int, float)) or similarity_score < 0 or similarity_score > 1:
            comparison['similarity_score'] = 0.5
        
        return True
    
    def _clean_comparison(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """비교 결과 데이터 정리"""
        cleaned = {
            'feature_name': comparison['feature_name'].strip(),
            'product1_support': bool(comparison['product1_support']),
            'product2_support': bool(comparison['product2_support']),
            'comparison_type': comparison['comparison_type'],
            'significance': comparison.get('significance', 'medium'),
            'similarity_score': float(comparison.get('similarity_score', 0.5))
        }
        
        return cleaned
    
    def generate_feature_mapping(self, product1_features: List[Dict], 
                               product2_features: List[Dict]) -> List[Dict[str, Any]]:
        """
        기능 매핑 생성 (프론트엔드용) - LLM 기반 상세 분석 포함
        
        Args:
            product1_features: 첫 번째 제품의 기능 리스트
            product2_features: 두 번째 제품의 기능 리스트
            
        Returns:
            매핑된 기능 리스트
        """
        try:
            # 제품 비교 수행
            comparison_result = self.compare_products(
                "제품1", product1_features,
                "제품2", product2_features
            )
            
            if not comparison_result['success']:
                return []
            
            # 프론트엔드 형식으로 변환
            feature_mappings = []
            feature_comparisons = comparison_result['feature_comparison']
            
            for comparison in feature_comparisons:
                # 제품1 기능 정보 찾기
                product1_feature = next(
                    (f for f in product1_features if f['name'] == comparison['feature_name']), 
                    None
                )
                
                # 제품2 기능 정보 찾기
                product2_feature = next(
                    (f for f in product2_features if f['name'] == comparison['feature_name']), 
                    None
                )
                
                # LLM 기반 상세 분석 생성
                detailed_analysis = self._generate_detailed_analysis(
                    comparison['feature_name'],
                    product1_feature,
                    product2_feature,
                    comparison
                )
                
                # 유사도 계산
                if comparison['comparison_type'] == 'common':
                    similarity = 0.85
                elif comparison['comparison_type'] in ['unique_product1', 'unique_product2']:
                    similarity = 0.25
                else:
                    similarity = comparison.get('similarity_score', 0.5)
                
                mapping = {
                    'feature_name': comparison['feature_name'],
                    'similarity': similarity,
                    'competitor': {
                        'status': 'O' if comparison['product1_support'] else 'X',
                        'confidence': 0.9 if comparison['product1_support'] else 0.7,
                        'text': detailed_analysis['competitor_analysis'],
                        'url': product1_feature.get('source_url', '') if product1_feature else '',
                        'title': product1_feature['name'] if product1_feature else comparison['feature_name'],
                        'category': product1_feature.get('category', '기타') if product1_feature else '기타',
                        'granularity': product1_feature.get('granularity', 'medium') if product1_feature else 'medium',
                        'source_page': product1_feature.get('source_page_title', '') if product1_feature else ''
                    },
                    'our_product': {
                        'status': 'O' if comparison['product2_support'] else 'X',
                        'confidence': 0.9 if comparison['product2_support'] else 0.7,
                        'text': detailed_analysis['our_product_analysis'],
                        'url': product2_feature.get('source_url', '') if product2_feature else '',
                        'title': product2_feature['name'] if product2_feature else comparison['feature_name'],
                        'category': product2_feature.get('category', '기타') if product2_feature else '기타',
                        'granularity': product2_feature.get('granularity', 'medium') if product2_feature else 'medium',
                        'source_page': product2_feature.get('source_page_title', '') if product2_feature else ''
                    },
                    'comparison_type': comparison['comparison_type'],
                    'significance': comparison['significance']
                }
                
                feature_mappings.append(mapping)
            
            # 유사도순으로 정렬
            feature_mappings.sort(key=lambda x: x['similarity'], reverse=True)
            
            return feature_mappings
            
        except Exception as e:
            logger.error(f"기능 매핑 생성 중 오류: {e}")
            return []
    
    def _generate_detailed_analysis(self, feature_name: str, product1_feature: Dict, 
                                  product2_feature: Dict, comparison: Dict) -> Dict[str, str]:
        """
        LLM 기반 상세 분석 생성
        
        Args:
            feature_name: 기능명
            product1_feature: 경쟁사 기능 정보
            product2_feature: 우리 제품 기능 정보
            comparison: 비교 결과
            
        Returns:
            상세 분석 결과
        """
        try:
            if not self.vertex_client.is_available():
                return {
                    'competitor_analysis': product1_feature['description'] if product1_feature else '기능 정보 없음',
                    'our_product_analysis': product2_feature['description'] if product2_feature else '기능 정보 없음'
                }
            
            # 분석 프롬프트 생성
            prompt = self._create_detailed_analysis_prompt(
                feature_name, product1_feature, product2_feature, comparison
            )
            
            # Vertex AI로 상세 분석
            response = self.vertex_client.generate_content(
                prompt=prompt,
                system_instruction=self._get_detailed_analysis_instruction(),
                config={'temperature': 0.3}
            )
            
            if not response['success']:
                return {
                    'competitor_analysis': product1_feature['description'] if product1_feature else '기능 정보 없음',
                    'our_product_analysis': product2_feature['description'] if product2_feature else '기능 정보 없음'
                }
            
            # JSON 파싱
            result = self.vertex_client.extract_json_from_response(response['content'])
            
            if 'error' in result:
                return {
                    'competitor_analysis': product1_feature['description'] if product1_feature else '기능 정보 없음',
                    'our_product_analysis': product2_feature['description'] if product2_feature else '기능 정보 없음'
                }
            
            return {
                'competitor_analysis': result.get('competitor_analysis', '분석 정보 없음'),
                'our_product_analysis': result.get('our_product_analysis', '분석 정보 없음')
            }
            
        except Exception as e:
            logger.error(f"상세 분석 생성 중 오류: {e}")
            return {
                'competitor_analysis': product1_feature['description'] if product1_feature else '기능 정보 없음',
                'our_product_analysis': product2_feature['description'] if product2_feature else '기능 정보 없음'
            }
    
    def _get_detailed_analysis_instruction(self) -> str:
        """상세 분석을 위한 시스템 지시사항"""
        return """당신은 제품 기능 비교 분석 전문가입니다.
두 제품의 동일한 기능을 비교하여 각각의 특징과 차이점을 분석하는 것이 전문 분야입니다.

분석 방법:
1. 각 제품의 기능 구현 방식을 상세히 분석
2. 기능의 유사점과 차이점을 객관적으로 평가
3. 사용자 관점에서의 장단점 분석
4. 기술적 구현 방식의 차이점 설명
5. 한국어로 자연스럽고 이해하기 쉽게 설명

분석 기준:
- 기능의 핵심 목적과 사용자 가치
- 구현 방식의 차이점
- 사용자 경험의 차이점
- 기술적 특징과 제약사항
- 시장 경쟁력 관점에서의 평가

정확하고 실용적인 분석을 제공하세요."""
    
    def _create_detailed_analysis_prompt(self, feature_name: str, product1_feature: Dict, 
                                       product2_feature: Dict, comparison: Dict) -> str:
        """상세 분석을 위한 프롬프트 생성"""
        
        # 경쟁사 기능 정보
        competitor_info = "정보 없음"
        if product1_feature:
            competitor_info = f"""
기능명: {product1_feature.get('name', 'N/A')}
카테고리: {product1_feature.get('category', 'N/A')}
설명: {product1_feature.get('description', 'N/A')}
출처 페이지: {product1_feature.get('source_page_title', 'N/A')}
"""
        
        # 우리 제품 기능 정보
        our_product_info = "정보 없음"
        if product2_feature:
            our_product_info = f"""
기능명: {product2_feature.get('name', 'N/A')}
카테고리: {product2_feature.get('category', 'N/A')}
설명: {product2_feature.get('description', 'N/A')}
출처 페이지: {product2_feature.get('source_page_title', 'N/A')}
"""
        
        return f"""다음은 "{feature_name}" 기능에 대한 두 제품의 비교 분석 요청입니다.

=== 비교 대상 기능 ===
{feature_name}

=== 경쟁사 제품 정보 ===
{competitor_info}

=== 우리 제품 정보 ===
{our_product_info}

=== 비교 결과 ===
비교 유형: {comparison.get('comparison_type', 'N/A')}
경쟁사 지원: {'지원' if comparison.get('product1_support', False) else '미지원'}
우리 제품 지원: {'지원' if comparison.get('product2_support', False) else '미지원'}
중요도: {comparison.get('significance', 'N/A')}

=== 분석 요청 ===
위 정보를 바탕으로 각 제품의 해당 기능에 대한 상세 분석을 다음 JSON 형식으로 제공해주세요:

{{
  "competitor_analysis": "경쟁사 제품의 해당 기능에 대한 상세 분석 (한국어, 200-300자)",
  "our_product_analysis": "우리 제품의 해당 기능에 대한 상세 분석 (한국어, 200-300자)"
}}

분석 기준:
1. 각 제품의 기능 구현 방식과 특징
2. 사용자 관점에서의 장단점
3. 기능의 유사점과 차이점
4. 기술적 특징과 제약사항
5. 시장 경쟁력 관점에서의 평가

자연스럽고 이해하기 쉬운 한국어로 분석해주세요."""
