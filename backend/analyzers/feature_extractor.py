"""
기능 추출기
텍스트에서 세부적인 제품 기능을 추출하고 한국어로 번역
"""

import json
import logging
from typing import Dict, List, Any, Optional
from .vertex_client import VertexAIClient

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """기능 추출기"""
    
    def __init__(self, vertex_client: VertexAIClient = None):
        """
        기능 추출기 초기화
        
        Args:
            vertex_client: Vertex AI 클라이언트
        """
        self.vertex_client = vertex_client or VertexAIClient()
        
        # 기능 카테고리 정의
        self.feature_categories = [
            'UI_UX', '보안', '통합', '성능', '관리', '분석', '커뮤니케이션', 
            '파일관리', '알림', '설정', '자동화', '백업', '동기화', '검색', '기타'
        ]
        
        # 시스템 지시사항
        self.system_instruction = """당신은 제품 기능 분석 및 번역 전문가입니다.
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
    
    def extract_features_from_text(self, company_name: str, help_text: str) -> Dict[str, Any]:
        """
        도움말 텍스트에서 세부적인 제품 기능을 추출하고 한국어로 번역
        
        Args:
            company_name: 회사명
            help_text: 분석할 도움말 텍스트
            
        Returns:
            추출된 기능 정보 딕셔너리
        """
        if not self.vertex_client.is_available():
            return {
                'success': False,
                'error': 'Vertex AI 서비스를 사용할 수 없습니다.',
                'extracted_features': [],
                'analysis_summary': {}
            }
        
        try:
            # 프롬프트 생성
            prompt = self._create_extraction_prompt(company_name, help_text)
            
            # Vertex AI로 기능 추출
            response = self.vertex_client.generate_content(
                prompt=prompt,
                system_instruction=self.system_instruction,
                config={'temperature': 0.2}  # 더 일관된 결과를 위해 낮은 온도
            )
            
            if not response['success']:
                return {
                    'success': False,
                    'error': response['error'],
                    'extracted_features': [],
                    'analysis_summary': {}
                }
            
            # JSON 파싱
            result = self.vertex_client.extract_json_from_response(response['content'])
            
            if 'error' in result:
                return {
                    'success': False,
                    'error': result['error'],
                    'extracted_features': [],
                    'analysis_summary': {}
                }
            
            # 결과 검증 및 정리
            validated_result = self._validate_and_clean_features(result)
            
            logger.info(f"{company_name}에서 {len(validated_result.get('extracted_features', []))}개 기능 추출 완료")
            
            return {
                'success': True,
                'extracted_features': validated_result.get('extracted_features', []),
                'analysis_summary': validated_result.get('analysis_summary', {}),
                'raw_response': response['content'][:500] + '...' if len(response['content']) > 500 else response['content']
            }
            
        except Exception as e:
            error_msg = f"기능 추출 중 오류: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'extracted_features': [],
                'analysis_summary': {}
            }
    
    def _create_extraction_prompt(self, company_name: str, help_text: str) -> str:
        """기능 추출을 위한 프롬프트 생성"""
        return f"""다음은 {company_name}의 제품 도움말 문서입니다. 이 텍스트에서 세부적인 제품 기능들을 추출하고 분류해주세요.

=== 도움말 문서 내용 ===
{help_text}

=== 분석 요청 ===
위 문서에서 구체적이고 세부적인 제품 기능을 추출하여 다음 JSON 형식으로 응답해주세요:

{{
  "extracted_features": [
    {{
      "name": "세부 기능명 (예: 챗봇 디자인 커스터마이징, PDF 내보내기, 실시간 알림 설정 등)",
      "category": "UI_UX|보안|통합|성능|관리|분석|커뮤니케이션|파일관리|알림|설정|자동화|백업|동기화|검색|기타",
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
- 데이터 백업 스케줄링
- 테마 색상 변경
- 폰트 크기 조정
- 자동 저장 간격 설정"""
    
    def _validate_and_clean_features(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """추출된 기능 검증 및 정리"""
        try:
            extracted_features = result.get('extracted_features', [])
            analysis_summary = result.get('analysis_summary', {})
            
            # 기능 검증 및 정리
            validated_features = []
            for feature in extracted_features:
                if self._is_valid_feature(feature):
                    cleaned_feature = self._clean_feature(feature)
                    validated_features.append(cleaned_feature)
            
            # 분석 요약 업데이트
            analysis_summary['total_features'] = len(validated_features)
            analysis_summary['validated_features'] = len(validated_features)
            
            return {
                'extracted_features': validated_features,
                'analysis_summary': analysis_summary
            }
            
        except Exception as e:
            logger.error(f"기능 검증 중 오류: {e}")
            return result
    
    def _is_valid_feature(self, feature: Dict[str, Any]) -> bool:
        """기능 유효성 검사"""
        required_fields = ['name', 'category', 'description']
        
        # 필수 필드 확인
        for field in required_fields:
            if field not in feature or not feature[field]:
                return False
        
        # 이름 길이 확인
        if len(feature['name']) < 3 or len(feature['name']) > 100:
            return False
        
        # 카테고리 유효성 확인
        if feature['category'] not in self.feature_categories:
            feature['category'] = '기타'
        
        # 신뢰도 확인
        confidence = feature.get('confidence', 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            feature['confidence'] = 0.5
        
        return True
    
    def _clean_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """기능 데이터 정리"""
        cleaned = {
            'name': feature['name'].strip(),
            'category': feature['category'],
            'description': feature['description'].strip(),
            'confidence': float(feature.get('confidence', 0.5)),
            'granularity': feature.get('granularity', 'medium')
        }
        
        # 설명 길이 제한
        if len(cleaned['description']) > 500:
            cleaned['description'] = cleaned['description'][:497] + '...'
        
        return cleaned
    
    def extract_features_from_pages(self, company_name: str, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 페이지에서 기능 추출
        
        Args:
            company_name: 회사명
            pages: 페이지 리스트 (각 페이지는 title, content, url 포함)
            
        Returns:
            추출된 기능 리스트
        """
        all_features = []
        
        for i, page in enumerate(pages):
            logger.info(f"페이지 {i+1}/{len(pages)} 분석 중: {page.get('title', '제목 없음')}")
            
            page_content = page.get('content', '')
            if len(page_content) < 50:
                continue
            
            # 페이지별 분석 텍스트 생성
            analysis_text = f"페이지 제목: {page.get('title', '제목 없음')}\n\n콘텐츠:\n{page_content[:2000]}"
            
            # 기능 추출
            result = self.extract_features_from_text(
                f"{company_name} - {page.get('title', '제목 없음')}", 
                analysis_text
            )
            
            if result['success']:
                features = result['extracted_features']
                logger.info(f"  - {len(features)}개 기능 발견")
                
                # 페이지 정보 추가
                for feature in features:
                    feature['source_url'] = page.get('url', '')
                    feature['source_page_title'] = page.get('title', '')
                
                all_features.extend(features)
        
        # 중복 제거
        unique_features = self._remove_duplicate_features(all_features)
        logger.info(f"총 {len(unique_features)}개 고유 기능 추출 완료")
        
        return unique_features
    
    def _remove_duplicate_features(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """중복 기능 제거"""
        unique_features = []
        seen_names = set()
        
        for feature in features:
            name = feature['name'].lower().strip()
            if name not in seen_names:
                unique_features.append(feature)
                seen_names.add(name)
        
        return unique_features
