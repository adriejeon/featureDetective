#!/usr/bin/env python3
"""
개선된 통합 기능 탐지 서비스 - 다중 제품 분석 및 정확한 링크 매핑
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from collections import defaultdict

from .crawlee_crawler_service import RecursiveCrawlerService
from .vertex_ai_service import VertexAIService

logger = logging.getLogger(__name__)

class FeatureDetectionService:
    """개선된 통합 기능 탐지 서비스"""
    
    def __init__(self):
        self.crawler = RecursiveCrawlerService()
        self.vertex_ai = VertexAIService()
        self.project_id = os.getenv('VERTEX_AI_PROJECT_ID', 'groobee-ai')
        # Vertex AI 분석 서비스 추가
        from .vertex_ai_analysis_service import VertexAIAnalysisService
        self.vertex_ai_analysis = VertexAIAnalysisService()
        
        # 분석 방법 결정
        if self.vertex_ai_analysis.is_available:
            self.analysis_method = "vertex_ai"
            logger.info("Vertex AI 분석 모드로 설정")
        else:
            self.analysis_method = "local_analysis"
            logger.info("로컬 분석 모드로 설정")
        
    async def detect_features_from_urls(self, 
                                      competitor_urls: List[str], 
                                      our_product_urls: List[str],
                                      project_name: str = "기능 탐지 프로젝트",
                                      product_names: List[str] = None) -> Dict[str, Any]:
        """
        URL 목록에서 기능을 탐지하고 분석 (개선된 버전)
        
        Args:
            competitor_urls: 경쟁사 URL 목록
            our_product_urls: 우리 제품 URL 목록
            project_name: 프로젝트 이름
            product_names: 제품명 목록 (선택사항)
            
        Returns:
            통합 분석 결과
        """
        try:
            logger.info(f"개선된 기능 탐지 시작: {project_name}")
            start_time = datetime.now()
            
            # 모든 URL을 하나의 리스트로 통합 (다중 제품 분석)
            all_urls = competitor_urls + our_product_urls
            
            # 제품명이 제공되지 않은 경우 기본값 사용
            if product_names is None:
                product_names = [f"제품{i+1}" for i in range(len(all_urls))]
            elif len(product_names) < len(all_urls):
                # 제품명이 부족한 경우 나머지는 기본값으로 채움
                for i in range(len(product_names), len(all_urls)):
                    product_names.append(f"제품{i+1}")
            
            # 1단계: 모든 제품 웹사이트 크롤링
            logger.info("모든 제품 웹사이트 크롤링 시작...")
            all_product_data = {}
            
            for i, url in enumerate(all_urls):
                try:
                    crawled_data = await self.crawler.crawl_website(url)
                    all_product_data[product_names[i]] = {
                        'url': url,
                        'data': crawled_data
                    }
                    logger.info(f"제품 {i+1} 크롤링 완료: {url} ({len(crawled_data)}개 페이지)")
                except Exception as e:
                    logger.error(f"제품 {i+1} 크롤링 실패: {url}, 오류: {e}")
                    all_product_data[product_names[i]] = {
                        'url': url,
                        'data': []
                    }
            
            # 2단계: 각 제품별 기능 분석 (Vertex AI 분석 서비스 사용)
            logger.info("각 제품별 Vertex AI 기능 분석 시작...")
            product_features = {}
            
            for product_name, product_info in all_product_data.items():
                if product_info['data']:
                    # Vertex AI 분석 서비스 사용 - 로컬 분석 모드로 전환
                    if not self.vertex_ai_analysis.is_available:
                        # 로컬 분석 사용
                        features = self.vertex_ai_analysis._extract_features_locally(
                            product_info['data'], 
                            product_name
                        )
                    else:
                        # Vertex AI 사용 - 제품 특성 분석 포함
                        features = await self.vertex_ai_analysis._extract_features_from_data(
                            product_info['data'], 
                            product_name
                        )
                    product_features[product_name] = features
                else:
                    product_features[product_name] = {
                        'extracted_features': [],
                        'analysis_summary': {
                            'total_features': 0,
                            'main_categories': [],
                            'document_quality': 'low'
                        },
                        'product_analysis': {
                            'product_characteristics': {
                                'product_type': '알 수 없음',
                                'target_audience': '알 수 없음',
                                'core_value_proposition': '알 수 없음',
                                'key_strengths': []
                            },
                            'feature_analysis': {
                                'most_important_features': []
                            }
                        }
                    }
            
            # 3단계: 모든 기능 병합 및 중복 제거
            logger.info("기능 병합 및 중복 제거 시작...")
            all_features = []
            for product_name, features in product_features.items():
                for feature in features.get('extracted_features', []):
                    feature['product_name'] = product_name
                    all_features.append(feature)
            
            # 중복 제거
            merged_features = self.vertex_ai.merge_and_deduplicate_features(all_features)
            
            # 4단계: 제품별 기능 매핑
            logger.info("제품별 기능 매핑 시작...")
            product_feature_mapping = self._map_features_to_products(merged_features, product_features)
            
            # 5단계: 결과 통합
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # 프론트엔드 호환성을 위한 구조 변환
            product_names = list(product_features.keys())
            competitor_features = product_features.get(product_names[0] if len(product_names) > 0 else '제품1', {})
            our_product_features = product_features.get(product_names[1] if len(product_names) > 1 else '제품2', {})
            third_product_features = product_features.get(product_names[2] if len(product_names) > 2 else '제품3', {})
            
            # 크롤링 결과에 기능 데이터 추가
            for product_name in all_product_data.keys():
                if product_name in product_features:
                    all_product_data[product_name]['features'] = product_features[product_name]
                else:
                    all_product_data[product_name]['features'] = {
                        'extracted_features': [],
                        'analysis_summary': {
                            'total_features': 0,
                            'main_categories': [],
                            'document_quality': 'low'
                        }
                    }
            
            # 비교 분석 결과 생성 (3개 제품 지원)
            comparison_analysis = self._generate_comparison_analysis(
                competitor_features, our_product_features, merged_features, product_feature_mapping, third_product_features, product_names
            )
            
            result = {
                'project_info': {
                    'name': project_name,
                    'created_at': start_time.isoformat(),
                    'processing_time_seconds': processing_time,
                    'total_products': len(all_urls),
                    'total_pages_crawled': sum(len(info['data']) for info in all_product_data.values())
                },
                'crawling_results': {
                    'product_data': all_product_data,
                    'total_urls': len(all_urls)
                },
                'analysis_results': {
                    'competitor_features': competitor_features,
                    'our_product_features': our_product_features,
                    'product_features': product_features,
                    'merged_features': merged_features,
                    'product_feature_mapping': product_feature_mapping,
                    'comparison_analysis': comparison_analysis,
                    'analysis_method': self.analysis_method
                },
                'summary': {
                    'total_unique_features': len(merged_features),
                    'total_products_analyzed': len(all_urls),
                    'analysis_quality': self._assess_analysis_quality(all_product_data)
                }
            }
            
            logger.info(f"개선된 기능 탐지 완료: {project_name} (처리 시간: {processing_time:.2f}초)")
            return result
            
        except Exception as e:
            logger.error(f"기능 탐지 중 오류: {e}")
            return {
                'error': str(e),
                'success': False,
                'project_name': project_name
            }
    
    async def _analyze_product_features(self, product_name: str, crawled_data: List[Dict], source_url: str) -> Dict[str, Any]:
        """개별 제품의 기능 분석"""
        try:
            if not crawled_data:
                return {
                    'extracted_features': [],
                    'analysis_summary': {
                        'total_features': 0,
                        'main_categories': [],
                        'document_quality': 'low'
                    }
                }
            
            # 각 페이지별로 개별 분석 (정확한 링크 매핑을 위해)
            all_features = []
            
            for page_data in crawled_data:
                if 'content' in page_data and page_data['content']:
                    # 개별 페이지 분석
                    page_features = self.vertex_ai.extract_features_from_text(
                        product_name, 
                        page_data['content'], 
                        page_data.get('url', source_url)
                    )
                    
                    # 각 기능에 페이지 정보 추가
                    for feature in page_features.get('extracted_features', []):
                        feature['source_page_url'] = page_data.get('url', source_url)
                        feature['source_page_title'] = page_data.get('title', '')
                        all_features.append(feature)
            
            # 중복 제거
            unique_features = self.vertex_ai.merge_and_deduplicate_features(all_features)
            
            # 요약 생성
            summary = self.vertex_ai.generate_feature_summary(unique_features)
            
            logger.info(f"{product_name} 기능 분석 완료: {len(unique_features)}개 기능")
            
            return {
                'extracted_features': unique_features,
                'analysis_summary': summary
            }
            
        except Exception as e:
            logger.error(f"{product_name} 기능 분석 오류: {e}")
            return {
                'extracted_features': [],
                'analysis_summary': {
                    'total_features': 0,
                    'main_categories': [],
                    'document_quality': 'low',
                    'error': str(e)
                }
            }
    
    def _map_features_to_products(self, merged_features: List[Dict], product_features: Dict) -> Dict[str, Dict]:
        """기능을 제품별로 매핑 (개선된 버전)"""
        product_feature_mapping = {}
        
        logger.info(f"=== 기능 매핑 시작 ===")
        logger.info(f"병합된 기능 수: {len(merged_features)}")
        logger.info(f"제품 수: {len(product_features)}")
        
        for product_name in product_features.keys():
            logger.info(f"제품 '{product_name}' 매핑 시작")
            product_feature_mapping[product_name] = {}
            
            product_extracted_features = product_features[product_name].get('extracted_features', [])
            logger.info(f"제품 '{product_name}' 추출된 기능 수: {len(product_extracted_features)}")
            
            for feature in merged_features:
                feature_name = feature.get('name', '')
                if feature_name:
                    logger.info(f"기능 '{feature_name}' 매핑 시도")
                    
                    # 해당 제품에서 이 기능이 발견되었는지 확인 (유사도 기반)
                    best_match = self._find_best_feature_match(
                        feature_name, 
                        product_extracted_features
                    )
                    
                    if best_match:
                        logger.info(f"기능 '{feature_name}' 최고 매칭 유사도: {best_match['similarity']:.3f}")
                    
                    # 유사도 임계값을 더 낮춰서 더 많은 매칭 허용 (0.1 -> 0.05)
                    if best_match and best_match['similarity'] > 0.05:  # 5% 이상 유사도
                        logger.info(f"기능 '{feature_name}' 매칭 성공 (유사도: {best_match['similarity']:.3f})")
                        product_feature_mapping[product_name][feature_name] = {
                            'status': 'O',
                            'description': best_match['feature'].get('description', feature.get('description', '')),
                            'source_url': best_match['feature'].get('source_page_url', ''),
                            'confidence': best_match['feature'].get('confidence', 0.8),
                            'similarity': best_match['similarity']
                        }
                    else:
                        logger.info(f"기능 '{feature_name}' 매칭 실패 (최고 유사도: {best_match['similarity'] if best_match else 0:.3f})")
                        # 기능이 없을 때 더 구체적인 메시지 제공
                        product_feature_mapping[product_name][feature_name] = {
                            'status': 'X',
                            'description': f'{product_name}에서 "{feature_name}" 기능을 찾을 수 없습니다.',
                            'source_url': '',
                            'confidence': 0.0
                        }
        
        logger.info(f"=== 기능 매핑 완료 ===")
        return product_feature_mapping
    
    def _find_best_feature_match(self, target_feature_name: str, product_features: List[Dict]) -> Optional[Dict]:
        """가장 유사한 기능 찾기"""
        if not product_features:
            return None
        
        best_match = None
        best_similarity = 0
        
        for feature in product_features:
            feature_name = feature.get('name', '')
            if feature_name:
                similarity = self._calculate_similarity(target_feature_name, feature_name)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = {
                        'feature': feature,
                        'similarity': similarity
                    }
        
        return best_match
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (개선된 버전)"""
        from difflib import SequenceMatcher
        
        # 정규화
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # 완전 일치 체크
        if text1 == text2:
            return 1.0
        
        # 부분 일치 체크
        if text1 in text2 or text2 in text1:
            return 0.9
        
        # SequenceMatcher 사용
        similarity = SequenceMatcher(None, text1, text2).ratio()
        
        # 키워드 기반 추가 점수
        keywords1 = set(text1.split())
        keywords2 = set(text2.split())
        
        if keywords1 and keywords2:
            keyword_similarity = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
            # 가중 평균 (키워드 유사도에 더 높은 가중치)
            final_similarity = (similarity * 0.3) + (keyword_similarity * 0.7)
        else:
            final_similarity = similarity
        
        # 동의어 매칭 추가 점수
        synonym_bonus = self._check_synonym_similarity(text1, text2)
        final_similarity = min(1.0, final_similarity + synonym_bonus)
        
        # 디버깅을 위한 로그 추가 (모든 유사도 계산 로그)
        logger.info(f"유사도 계산: '{text1}' vs '{text2}' = {final_similarity:.3f}")
        
        # 높은 유사도일 때 추가 정보
        if final_similarity > 0.3:
            logger.info(f"높은 유사도 발견: '{text1}' vs '{text2}' = {final_similarity:.3f}")
        
        return final_similarity
    
    def _check_synonym_similarity(self, text1: str, text2: str) -> float:
        """동의어 기반 유사도 보너스 점수"""
        # 기능별 동의어 사전 (확장된 버전)
        feature_synonyms = {
            'chat': ['채팅', '메시지', '대화', 'message', 'messaging', '커뮤니케이션'],
            'message': ['메시지', '채팅', '대화', 'chat', 'messaging', '커뮤니케이션'],
            'file': ['파일', '문서', 'document', 'upload', '첨부'],
            'upload': ['업로드', '파일', 'upload', 'file', '첨부'],
            'download': ['다운로드', 'download', '파일', '저장'],
            'search': ['검색', 'search', 'find', '찾기', '검색기능'],
            'setting': ['설정', 'setting', 'config', 'configuration', '관리'],
            'notification': ['알림', 'notification', 'alert', '알림', '공지'],
            'security': ['보안', 'security', 'safety', 'protection', '안전'],
            'api': ['api', '연동', 'integration', 'interface', '통합'],
            'mobile': ['모바일', 'mobile', 'phone', '스마트폰', '휴대폰'],
            'desktop': ['데스크톱', 'desktop', 'pc', '컴퓨터', 'pc앱'],
            'voice': ['음성', 'voice', 'audio', '통화', '음성통화'],
            'video': ['비디오', 'video', '화상', '영상', '화상통화'],
            'meeting': ['회의', 'meeting', 'conference', '화상회의', '컨퍼런스'],
            'bot': ['봇', 'bot', '자동화', 'automation', '자동'],
            'permission': ['권한', 'permission', 'access', 'authorization', '접근'],
            'backup': ['백업', 'backup', '복원', 'restore', '저장'],
            'sync': ['동기화', 'sync', 'synchronization', '동기'],
            'analytics': ['분석', 'analytics', '통계', 'statistics', '데이터'],
            'monitoring': ['모니터링', 'monitoring', '감시', '추적', '데이터 모니터링'],
            'data': ['데이터', 'data', '정보', '자료'],
            'report': ['리포트', 'report', '보고서', '통계'],
            'dashboard': ['대시보드', 'dashboard', '현황', '개요'],
            'user': ['사용자', 'user', '계정', 'account', '멤버'],
            'team': ['팀', 'team', '그룹', 'group', '조직'],
            'channel': ['채널', 'channel', '방', 'room', '공간'],
            'server': ['서버', 'server', '워크스페이스', 'workspace'],
            'integration': ['통합', 'integration', '연동', '연결', 'connect'],
            'automation': ['자동화', 'automation', '자동', 'auto', '봇'],
            'workflow': ['워크플로우', 'workflow', '프로세스', 'process', '흐름']
        }
        
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # 동의어 매칭 확인
        for main_word, synonyms in feature_synonyms.items():
            if main_word in text1_lower or any(syn in text1_lower for syn in synonyms):
                if main_word in text2_lower or any(syn in text2_lower for syn in synonyms):
                    return 0.4  # 동의어 매칭 시 40% 보너스 (증가)
        
        return 0.0
    
    def _combine_crawled_data(self, crawled_data: List[Dict]) -> str:
        """크롤링된 데이터 결합"""
        combined_text = ""
        for data in crawled_data:
            if 'content' in data and data['content']:
                combined_text += data['content'] + "\n\n"
        return combined_text.strip()
    
    def _assess_analysis_quality(self, product_data: Dict) -> str:
        """분석 품질 평가"""
        total_pages = sum(len(info['data']) for info in product_data.values())
        
        if total_pages == 0:
            return 'low'
        elif total_pages < 5:
            return 'medium'
        else:
            return 'high'
    
    async def analyze_single_url(self, url: str, company_name: str = "분석 대상") -> Dict[str, Any]:
        """
        단일 URL에서 기능 분석
        
        Args:
            url: 분석할 URL
            company_name: 회사명
            
        Returns:
            기능 분석 결과
        """
        try:
            logger.info(f"단일 URL 분석 시작: {url}")
            
            # 크롤링
            crawled_data = await self.crawler.crawl_website(url)
            
            if not crawled_data:
                return {
                    'error': '크롤링된 데이터가 없습니다.',
                    'success': False
                }
            
            # 텍스트 결합
            combined_text = self._combine_crawled_data(crawled_data)
            
            # Vertex AI로 기능 분석
            features = self.vertex_ai.extract_features_from_text(company_name, combined_text)
            
            result = {
                'url': url,
                'company_name': company_name,
                'pages_crawled': len(crawled_data),
                'features': features,
                'success': True
            }
            
            logger.info(f"단일 URL 분석 완료: {url} ({len(features.get('extracted_features', []))}개 기능)")
            return result
            
        except Exception as e:
            logger.error(f"단일 URL 분석 오류: {e}")
            return {
                'error': str(e),
                'success': False,
                'url': url
            }
    
    async def analyze_keyword_support(self, url: str, keyword: str) -> Dict[str, Any]:
        """
        특정 URL에서 키워드 지원 여부 분석
        
        Args:
            url: 분석할 URL
            keyword: 분석할 키워드
            
        Returns:
            키워드 지원 분석 결과
        """
        try:
            logger.info(f"키워드 지원 분석 시작: {url} - {keyword}")
            
            # 크롤링
            crawled_data = await self.crawler.crawl_website(url)
            
            if not crawled_data:
                return {
                    'error': '크롤링된 데이터가 없습니다.',
                    'success': False
                }
            
            # 텍스트 결합
            combined_text = self._combine_crawled_data(crawled_data)
            
            # Vertex AI로 키워드 분석
            analysis = self.vertex_ai.analyze_keyword_support(keyword, combined_text)
            
            result = {
                'url': url,
                'keyword': keyword,
                'analysis': analysis,
                'pages_crawled': len(crawled_data),
                'success': True
            }
            
            logger.info(f"키워드 지원 분석 완료: {keyword}")
            return result
            
        except Exception as e:
            logger.error(f"키워드 지원 분석 오류: {e}")
            return {
                'error': str(e),
                'success': False,
                'url': url,
                'keyword': keyword
            }

    def _generate_comparison_analysis(self, competitor_features: Dict, our_product_features: Dict, 
                                    merged_features: List[Dict], product_feature_mapping: Dict, 
                                    third_product_features: Dict = None, product_names: List[str] = None) -> Dict[str, Any]:
        """비교 분석 결과 생성 (3개 제품 지원)"""
        try:
            # 제품명 처리
            if product_names is None:
                product_names = ['제품1', '제품2', '제품3']
            elif len(product_names) < 3:
                for i in range(len(product_names), 3):
                    product_names.append(f'제품{i+1}')
            
            # 제품별 기능 수 계산
            competitor_feature_count = len(competitor_features.get('extracted_features', []))
            our_product_feature_count = len(our_product_features.get('extracted_features', []))
            third_product_feature_count = len(third_product_features.get('extracted_features', [])) if third_product_features else 0
            
            # 공통 기능 수 계산
            common_features = 0
            for feature in merged_features:
                feature_name = feature.get('name', '')
                if feature_name:
                    # 모든 제품에서 이 기능이 지원되는지 확인
                    all_supported = True
                    for product_name, feature_mapping in product_feature_mapping.items():
                        if feature_name in feature_mapping:
                            if feature_mapping[feature_name].get('status') != 'O':
                                all_supported = False
                                break
                        else:
                            all_supported = False
                            break
                    if all_supported:
                        common_features += 1
            
            # 비교 요약 생성
            comparison_summary = {
                'total_features_product1': competitor_feature_count,
                'total_features_product2': our_product_feature_count,
                'total_features_product3': third_product_feature_count,
                'common_features': common_features,
                'product1_unique': competitor_feature_count - common_features,
                'product2_unique': our_product_feature_count - common_features,
                'product3_unique': third_product_feature_count - common_features if third_product_features else 0,
                'product_names': product_names  # 실제 제품명 추가
            }
            
            # 경쟁 우위 분석
            competitive_analysis = {
                'product1_advantages': [],
                'product2_advantages': [],
                'product3_advantages': [],
                'recommendations': [],
                'product_names': product_names  # 실제 제품명 추가
            }
            
            # 각 제품의 고유 기능을 장점으로 추가
            for feature in merged_features:
                feature_name = feature.get('name', '')
                if feature_name:
                    # 제품1 고유 기능
                    if (feature_name in product_feature_mapping.get('제품1', {}) and 
                        product_feature_mapping['제품1'][feature_name].get('status') == 'O' and
                        (feature_name not in product_feature_mapping.get('제품2', {}) or
                        product_feature_mapping['제품2'][feature_name].get('status') != 'O') and
                        (feature_name not in product_feature_mapping.get('제품3', {}) or
                        product_feature_mapping['제품3'][feature_name].get('status') != 'O')):
                        competitive_analysis['product1_advantages'].append(feature_name)
                    
                    # 제품2 고유 기능
                    if (feature_name in product_feature_mapping.get('제품2', {}) and 
                        product_feature_mapping['제품2'][feature_name].get('status') == 'O' and
                        (feature_name not in product_feature_mapping.get('제품1', {}) or
                        product_feature_mapping['제품1'][feature_name].get('status') != 'O') and
                        (feature_name not in product_feature_mapping.get('제품3', {}) or
                        product_feature_mapping['제품3'][feature_name].get('status') != 'O')):
                        competitive_analysis['product2_advantages'].append(feature_name)
                    
                    # 제품3 고유 기능 (3개 제품이 있는 경우)
                    if third_product_features and (feature_name in product_feature_mapping.get('제품3', {}) and 
                        product_feature_mapping['제품3'][feature_name].get('status') == 'O' and
                        (feature_name not in product_feature_mapping.get('제품1', {}) or
                        product_feature_mapping['제품1'][feature_name].get('status') != 'O') and
                        (feature_name not in product_feature_mapping.get('제품2', {}) or
                        product_feature_mapping['제품2'][feature_name].get('status') != 'O')):
                        competitive_analysis['product3_advantages'].append(feature_name)
            
            # 개선 권장사항 생성
            if competitive_analysis['product1_advantages']:
                competitive_analysis['recommendations'].append(
                    f"{product_names[0]}의 고유 기능 {len(competitive_analysis['product1_advantages'])}개를 분석하여 차별화 전략 수립 필요"
                )
            
            if competitive_analysis['product2_advantages']:
                competitive_analysis['recommendations'].append(
                    f"{product_names[1]}의 고유 기능 {len(competitive_analysis['product2_advantages'])}개를 강화하여 경쟁 우위 확보"
                )
            
            if third_product_features and competitive_analysis['product3_advantages']:
                competitive_analysis['recommendations'].append(
                    f"{product_names[2]}의 고유 기능 {len(competitive_analysis['product3_advantages'])}개를 참고하여 시장 동향 파악"
                )
            
            if common_features > 0:
                competitive_analysis['recommendations'].append(
                    f"공통 기능 {common_features}개에 대해 사용자 경험 개선으로 차별화"
                )
            
            return {
                'comparison_summary': comparison_summary,
                'competitive_analysis': competitive_analysis
            }
            
        except Exception as e:
            logger.error(f"비교 분석 생성 오류: {e}")
            return {
                'comparison_summary': {
                    'total_features_product1': 0,
                    'total_features_product2': 0,
                    'total_features_product3': 0,
                    'common_features': 0,
                    'product1_unique': 0,
                    'product2_unique': 0,
                    'product3_unique': 0
                },
                'competitive_analysis': {
                    'product1_advantages': [],
                    'product2_advantages': [],
                    'product3_advantages': [],
                    'recommendations': []
                }
            }

# 동기 래퍼 함수들
def detect_features_from_urls_sync(competitor_urls: List[str], 
                                 our_product_urls: List[str],
                                 project_name: str = "기능 탐지 프로젝트") -> Dict[str, Any]:
    """동기적으로 기능 탐지"""
    return asyncio.run(FeatureDetectionService().detect_features_from_urls(
        competitor_urls, our_product_urls, project_name
    ))

def analyze_single_url_sync(url: str, company_name: str = "분석 대상") -> Dict[str, Any]:
    """동기적으로 단일 URL 분석"""
    return asyncio.run(FeatureDetectionService().analyze_single_url(url, company_name))

def analyze_keyword_support_sync(url: str, keyword: str) -> Dict[str, Any]:
    """동기적으로 키워드 지원 분석"""
    return asyncio.run(FeatureDetectionService().analyze_keyword_support(url, keyword))
