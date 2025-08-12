"""
분석 보고서 생성기
기능 분석 결과를 바탕으로 경쟁 분석 보고서 생성
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .vertex_client import VertexAIClient

logger = logging.getLogger(__name__)


class ReportGenerator:
    """분석 보고서 생성기"""
    
    def __init__(self, vertex_client: VertexAIClient = None):
        """
        보고서 생성기 초기화
        
        Args:
            vertex_client: Vertex AI 클라이언트
        """
        self.vertex_client = vertex_client or VertexAIClient()
        
        # 시스템 지시사항
        self.system_instruction = """당신은 경쟁사 분석 보고서 작성 전문가입니다.
기능 분석 결과를 바탕으로 실용적이고 인사이트 있는 경쟁 분석 보고서를 작성하는 것이 전문 분야입니다.

보고서 작성 기준:
1. 객관적이고 데이터 기반의 분석
2. 실용적인 인사이트와 권장사항
3. 명확하고 이해하기 쉬운 표현
4. 실행 가능한 개선 방안 제시
5. 시장 동향과 사용자 니즈 고려

보고서 구조:
- 실행 요약
- 주요 발견사항
- 경쟁 우위 분석
- 기능 격차 분석
- 개선 권장사항
- 시장 기회 분석

전문적이고 실용적인 보고서를 작성하세요."""
    
    def generate_competitive_analysis_report(self, competitor_name: str, our_product_name: str,
                                           competitor_features: List[Dict], our_product_features: List[Dict],
                                           comparison_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        경쟁 분석 보고서 생성
        
        Args:
            competitor_name: 경쟁사명
            our_product_name: 우리 제품명
            competitor_features: 경쟁사 기능 리스트
            our_product_features: 우리 제품 기능 리스트
            comparison_result: 비교 분석 결과
            
        Returns:
            생성된 보고서
        """
        if not self.vertex_client.is_available():
            return {
                'success': False,
                'error': 'Vertex AI 서비스를 사용할 수 없습니다.',
                'report': {}
            }
        
        try:
            # 프롬프트 생성
            prompt = self._create_report_prompt(competitor_name, our_product_name,
                                              competitor_features, our_product_features,
                                              comparison_result)
            
            # Vertex AI로 보고서 생성
            response = self.vertex_client.generate_content(
                prompt=prompt,
                system_instruction=self.system_instruction,
                config={'temperature': 0.4}
            )
            
            if not response['success']:
                return {
                    'success': False,
                    'error': response['error'],
                    'report': {}
                }
            
            # JSON 파싱
            result = self.vertex_client.extract_json_from_response(response['content'])
            
            if 'error' in result:
                return {
                    'success': False,
                    'error': result['error'],
                    'report': {}
                }
            
            # 보고서 메타데이터 추가
            report = self._add_report_metadata(result, competitor_name, our_product_name)
            
            logger.info(f"경쟁 분석 보고서 생성 완료: {competitor_name} vs {our_product_name}")
            
            return {
                'success': True,
                'report': report,
                'raw_response': response['content'][:500] + '...' if len(response['content']) > 500 else response['content']
            }
            
        except Exception as e:
            error_msg = f"보고서 생성 중 오류: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'report': {}
            }
    
    def _create_report_prompt(self, competitor_name: str, our_product_name: str,
                            competitor_features: List[Dict], our_product_features: List[Dict],
                            comparison_result: Dict[str, Any]) -> str:
        """보고서 생성을 위한 프롬프트 생성"""
        
        # 기능 요약 생성
        comp_features_summary = self._create_features_summary(competitor_features)
        our_features_summary = self._create_features_summary(our_product_features)
        
        # 비교 결과 요약
        comparison_summary = comparison_result.get('comparison_summary', {})
        competitive_analysis = comparison_result.get('competitive_analysis', {})
        
        return f"""다음은 {competitor_name}과 {our_product_name}의 경쟁 분석 보고서 작성 요청입니다.

=== {competitor_name} 기능 요약 ===
{comp_features_summary}

=== {our_product_name} 기능 요약 ===
{our_features_summary}

=== 비교 분석 결과 ===
비교 요약: {json.dumps(comparison_summary, ensure_ascii=False, indent=2)}
경쟁 분석: {json.dumps(competitive_analysis, ensure_ascii=False, indent=2)}

=== 보고서 작성 요청 ===
위 분석 결과를 바탕으로 다음 JSON 형식의 경쟁 분석 보고서를 작성해주세요:

{{
  "executive_summary": {{
    "overview": "전체 분석 개요",
    "key_findings": ["주요 발견사항들"],
    "recommendations": ["핵심 권장사항들"]
  }},
  "competitive_analysis": {{
    "market_positioning": "시장 포지셔닝 분석",
    "strengths_weaknesses": {{
      "competitor_strengths": ["경쟁사 강점들"],
      "competitor_weaknesses": ["경쟁사 약점들"],
      "our_strengths": ["우리 제품 강점들"],
      "our_weaknesses": ["우리 제품 약점들"]
    }},
    "competitive_advantages": ["경쟁 우위 요소들"]
  }},
  "feature_gap_analysis": {{
    "missing_features": ["우리 제품에 없는 기능들"],
    "unique_features": ["우리 제품만의 고유 기능들"],
    "improvement_opportunities": ["개선 기회들"],
    "priority_features": ["우선 개발 기능들"]
  }},
  "market_opportunities": {{
    "untapped_markets": ["미개발 시장 기회들"],
    "user_needs": ["사용자 니즈 분석"],
    "trend_analysis": "시장 트렌드 분석"
  }},
  "action_plan": {{
    "short_term": ["단기 실행 계획"],
    "medium_term": ["중기 실행 계획"],
    "long_term": ["장기 실행 계획"],
    "success_metrics": ["성공 지표들"]
  }}
}}

보고서 작성 기준:
1. 객관적이고 데이터 기반의 분석
2. 실용적인 인사이트와 권장사항
3. 명확하고 이해하기 쉬운 표현
4. 실행 가능한 개선 방안 제시
5. 시장 동향과 사용자 니즈 고려"""
    
    def _create_features_summary(self, features: List[Dict]) -> str:
        """기능 요약 생성"""
        if not features:
            return "기능 정보 없음"
        
        # 카테고리별 기능 분류
        categories = {}
        for feature in features:
            category = feature.get('category', '기타')
            if category not in categories:
                categories[category] = []
            categories[category].append(feature['name'])
        
        # 요약 생성
        summary_parts = []
        for category, feature_names in categories.items():
            summary_parts.append(f"{category}: {', '.join(feature_names[:5])}")
            if len(feature_names) > 5:
                summary_parts[-1] += f" 외 {len(feature_names) - 5}개"
        
        return "\n".join(summary_parts)
    
    def _add_report_metadata(self, report: Dict[str, Any], competitor_name: str, our_product_name: str) -> Dict[str, Any]:
        """보고서 메타데이터 추가"""
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'competitor_name': competitor_name,
            'our_product_name': our_product_name,
            'analysis_type': 'competitive_analysis',
            'report_version': '1.0'
        }
        
        report['metadata'] = metadata
        return report
    
    def generate_feature_comparison_table(self, feature_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        기능 비교 테이블 생성
        
        Args:
            feature_mappings: 기능 매핑 리스트
            
        Returns:
            비교 테이블 데이터
        """
        try:
            # 카테고리별 분류
            categories = {}
            for mapping in feature_mappings:
                category = mapping.get('product1', {}).get('category', '기타')
                if category not in categories:
                    categories[category] = []
                categories[category].append(mapping)
            
            # 테이블 데이터 생성
            table_data = {
                'categories': [],
                'summary': {
                    'total_features': len(feature_mappings),
                    'common_features': len([m for m in feature_mappings if m.get('comparison_type') == 'common']),
                    'unique_competitor': len([m for m in feature_mappings if m.get('comparison_type') == 'unique_product1']),
                    'unique_our_product': len([m for m in feature_mappings if m.get('comparison_type') == 'unique_product2'])
                }
            }
            
            for category, mappings in categories.items():
                category_data = {
                    'name': category,
                    'features': mappings,
                    'count': len(mappings)
                }
                table_data['categories'].append(category_data)
            
            return {
                'success': True,
                'table_data': table_data
            }
            
        except Exception as e:
            logger.error(f"기능 비교 테이블 생성 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'table_data': {}
            }
    
    def generate_executive_summary(self, comparison_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        실행 요약 생성
        
        Args:
            comparison_result: 비교 분석 결과
            
        Returns:
            실행 요약
        """
        try:
            comparison_summary = comparison_result.get('comparison_summary', {})
            competitive_analysis = comparison_result.get('competitive_analysis', {})
            
            summary = {
                'total_features_compared': comparison_summary.get('total_comparisons', 0),
                'common_features': comparison_summary.get('common_features', 0),
                'unique_features_competitor': comparison_summary.get('unique_features_product1', 0),
                'unique_features_our_product': comparison_summary.get('unique_features_product2', 0),
                'key_insights': competitive_analysis.get('recommendations', [])[:3],
                'market_positioning': competitive_analysis.get('market_positioning', '분석 중'),
                'generated_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"실행 요약 생성 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': {}
            }
