"""
개선된 Vertex AI Gemini 서비스 - 효율적인 기능 분석 및 중복 제거
"""

import json
import logging
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
import os
import re
from collections import defaultdict
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class VertexAIService:
    """
    개선된 Vertex AI Gemini 서비스
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
        self.model = os.getenv('VERTEX_AI_MODEL', 'gemini-2.5-pro')
        
        try:
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
            )
            logger.info(f"Vertex AI 클라이언트 초기화 완료: {self.project_id}")
        except Exception as e:
            logger.error(f"Vertex AI 클라이언트 초기화 실패: {e}")
            raise
    
    def extract_features_from_text(self, company_name: str, help_text: str, source_url: str = "") -> Dict[str, Any]:
        """
        도움말 텍스트에서 세부적인 제품 기능을 추출하고 한국어로 번역
        
        Args:
            company_name: 회사명
            help_text: 분석할 도움말 텍스트
            source_url: 소스 URL
            
        Returns:
            추출된 기능 정보 딕셔너리
        """
        try:
            # 텍스트 길이 제한 (토큰 절약)
            if len(help_text) > 3000:
                help_text = help_text[:3000] + "..."
            
            # 간단하고 명확한 프롬프트
            prompt_text = f"""다음 문서에서 제품 기능을 추출하세요:

{help_text}

JSON 형식으로 응답:
{{
  "extracted_features": [
    {{
      "name": "기능명",
      "category": "기타",
      "description": "기능 설명",
      "confidence": 0.9,
      "granularity": "medium"
    }}
  ]
}}"""

            # Vertex AI 호출 (올바른 API 사용)
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                )
            )
            
            # 응답 파싱 (개선된 버전)
            response_text = response.text.strip()
            logger.info(f"Vertex AI 원본 응답: {response_text[:200]}...")
            
            # JSON 추출 시도
            try:
                # ```json 블록에서 추출
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    if json_end != -1:
                        response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    if json_end != -1:
                        response_text = response_text[json_start:json_end].strip()
                
                # JSON 파싱
                result = json.loads(response_text)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 실패: {e}")
                logger.error(f"파싱 시도한 텍스트: {response_text}")
                
                # 폴백: 간단한 기능 추출
                result = self._fallback_feature_extraction(company_name, help_text, source_url)
            
            # 결과 검증 및 정리
            if 'extracted_features' in result:
                result['extracted_features'] = self._clean_and_validate_features(
                    result['extracted_features'], source_url
                )
            
            return result
            
        except Exception as e:
            logger.error(f"기능 추출 오류: {e}")
            return {
                'extracted_features': [],
                'error': str(e)
            }
    
    def _clean_and_validate_features(self, features: List[Dict], source_url: str) -> List[Dict]:
        """기능 목록 정리 및 검증"""
        cleaned_features = []
        
        for feature in features:
            if not isinstance(feature, dict):
                continue
                
            # 필수 필드 확인
            if 'name' not in feature or not feature['name']:
                continue
            
            # 기본값 설정
            cleaned_feature = {
                'name': feature.get('name', '').strip(),
                'category': feature.get('category', '기타'),
                'description': feature.get('description', '').strip(),
                'confidence': min(1.0, max(0.0, float(feature.get('confidence', 0.8)))),
                'granularity': feature.get('granularity', 'medium'),
                'source_url': source_url
            }
            
            # 설명이 없으면 이름으로 대체
            if not cleaned_feature['description']:
                cleaned_feature['description'] = cleaned_feature['name']
            
            cleaned_features.append(cleaned_feature)
        
        return cleaned_features[:20]  # 최대 20개만 반환
    
    def merge_and_deduplicate_features(self, all_features: List[Dict]) -> List[Dict]:
        """여러 제품의 기능을 병합하고 중복 제거"""
        if not all_features:
            return []
        
        # 기능명 기준으로 그룹화
        feature_groups = defaultdict(list)
        
        for feature in all_features:
            if 'name' not in feature:
                continue
            
            # 기능명 정규화 (대소문자, 공백 등)
            normalized_name = self._normalize_feature_name(feature['name'])
            feature_groups[normalized_name].append(feature)
        
        # 중복 제거 및 병합
        merged_features = []
        
        for normalized_name, features in feature_groups.items():
            if len(features) == 1:
                # 단일 기능
                merged_features.append(features[0])
            else:
                # 중복 기능 - 가장 좋은 설명 선택
                best_feature = self._select_best_feature(features)
                merged_features.append(best_feature)
        
        return merged_features
    
    def _normalize_feature_name(self, name: str) -> str:
        """기능명 정규화"""
        # 소문자 변환
        normalized = name.lower().strip()
        
        # 공백 정규화
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 특수문자 제거
        normalized = re.sub(r'[^\w\s가-힣]', '', normalized)
        
        return normalized
    
    def _select_best_feature(self, features: List[Dict]) -> Dict:
        """가장 좋은 기능 설명 선택"""
        if not features:
            return {}
        
        # 신뢰도가 높고 설명이 긴 것을 우선
        best_feature = max(features, key=lambda x: (
            float(x.get('confidence', 0)),
            len(x.get('description', ''))
        ))
        
        return best_feature
    
    def analyze_product_comparison(self, competitor_features: List[Dict], our_product_features: List[Dict]) -> Dict[str, Any]:
        """
        제품 간 기능 비교 분석
        
        Args:
            competitor_features: 경쟁사 기능 목록
            our_product_features: 우리 제품 기능 목록
            
        Returns:
            비교 분석 결과
        """
        try:
            # 기능명 정규화
            competitor_names = {self._normalize_feature_name(f['name']): f for f in competitor_features}
            our_names = {self._normalize_feature_name(f['name']): f for f in our_product_features}
            
            # 비교 분석
            comparison_results = []
            
            # 모든 기능에 대해 비교
            all_features = set(competitor_names.keys()) | set(our_names.keys())
            
            for feature_name in all_features:
                competitor_feature = competitor_names.get(feature_name)
                our_feature = our_names.get(feature_name)
                
                comparison = {
                    'feature_name': feature_name,
                    'competitor_has': competitor_feature is not None,
                    'our_product_has': our_feature is not None,
                    'competitor_description': competitor_feature.get('description', '') if competitor_feature else '',
                    'our_product_description': our_feature.get('description', '') if our_feature else '',
                    'competitor_url': competitor_feature.get('source_url', '') if competitor_feature else '',
                    'our_product_url': our_feature.get('source_url', '') if our_feature else '',
                }
                
                comparison_results.append(comparison)
            
            return {
                'comparison_results': comparison_results,
                'total_features': len(all_features),
                'competitor_unique': len(set(competitor_names.keys()) - set(our_names.keys())),
                'our_product_unique': len(set(our_names.keys()) - set(competitor_names.keys())),
                'common_features': len(set(competitor_names.keys()) & set(our_names.keys()))
            }
            
        except Exception as e:
            logger.error(f"제품 비교 분석 오류: {e}")
            return {
                'comparison_results': [],
                'error': str(e)
            }
    
    def generate_feature_summary(self, features: List[Dict]) -> Dict[str, Any]:
        """기능 요약 생성"""
        if not features:
            return {'summary': '분석된 기능이 없습니다.'}
        
        try:
            # 카테고리별 분류
            categories = defaultdict(list)
            for feature in features:
                category = feature.get('category', '기타')
                categories[category].append(feature)
            
            # 요약 생성
            summary = {
                'total_features': len(features),
                'categories': dict(categories),
                'main_categories': list(categories.keys()),
                'high_granularity_count': len([f for f in features if f.get('granularity') == 'high']),
                'average_confidence': sum(f.get('confidence', 0) for f in features) / len(features)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"기능 요약 생성 오류: {e}")
            return {'error': str(e)}
    
    def _fallback_feature_extraction(self, company_name: str, help_text: str, source_url: str) -> Dict[str, Any]:
        """JSON 파싱 실패 시 폴백 기능 추출"""
        try:
            # 간단한 키워드 기반 기능 추출
            feature_keywords = [
                '설정', '관리', '업로드', '다운로드', '검색', '필터', '정렬', '내보내기', '가져오기',
                '알림', '메시지', '채팅', '통화', '화상', '회의', '파일', '공유', '권한', '보안',
                '백업', '복원', '동기화', '연동', 'API', '웹훅', '자동화', '스케줄', '템플릿',
                '설정', '관리', 'upload', 'download', 'search', 'filter', 'sort', 'export', 'import',
                'notification', 'message', 'chat', 'call', 'video', 'meeting', 'file', 'share', 'permission', 'security',
                'backup', 'restore', 'sync', 'integration', 'api', 'webhook', 'automation', 'schedule', 'template'
            ]
            
            extracted_features = []
            help_text_lower = help_text.lower()
            
            for keyword in feature_keywords:
                if keyword.lower() in help_text_lower:
                    # 키워드 주변 텍스트 추출
                    keyword_pos = help_text_lower.find(keyword.lower())
                    start = max(0, keyword_pos - 50)
                    end = min(len(help_text), keyword_pos + len(keyword) + 50)
                    context = help_text[start:end].strip()
                    
                    extracted_features.append({
                        'name': keyword,
                        'category': '기타',
                        'description': f'{keyword} 관련 기능: {context}',
                        'confidence': 0.7,
                        'granularity': 'medium',
                        'source_url': source_url
                    })
            
            # 중복 제거
            unique_features = []
            seen_names = set()
            for feature in extracted_features:
                if feature['name'] not in seen_names:
                    unique_features.append(feature)
                    seen_names.add(feature['name'])
            
            return {
                'extracted_features': unique_features[:10]  # 최대 10개만
            }
            
        except Exception as e:
            logger.error(f"폴백 기능 추출 오류: {e}")
            return {
                'extracted_features': []
            }
