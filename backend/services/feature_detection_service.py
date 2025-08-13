#!/usr/bin/env python3
"""
통합 기능 탐지 서비스 - 크롤링 + Vertex AI 분석
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from .crawlee_crawler_service import RecursiveCrawlerService
from .vertex_ai_service import VertexAIService

logger = logging.getLogger(__name__)

class FeatureDetectionService:
    """통합 기능 탐지 서비스"""
    
    def __init__(self):
        self.crawler = RecursiveCrawlerService()
        self.vertex_ai = VertexAIService()
        self.project_id = os.getenv('VERTEX_AI_PROJECT_ID', 'groobee-ai')
        
    async def detect_features_from_urls(self, 
                                      competitor_urls: List[str], 
                                      our_product_urls: List[str],
                                      project_name: str = "기능 탐지 프로젝트") -> Dict[str, Any]:
        """
        URL 목록에서 기능을 탐지하고 분석
        
        Args:
            competitor_urls: 경쟁사 URL 목록
            our_product_urls: 우리 제품 URL 목록
            project_name: 프로젝트 이름
            
        Returns:
            통합 분석 결과
        """
        try:
            logger.info(f"기능 탐지 시작: {project_name}")
            start_time = datetime.now()
            
            # 1단계: 경쟁사 웹사이트 크롤링
            logger.info("경쟁사 웹사이트 크롤링 시작...")
            competitor_data = []
            for url in competitor_urls:
                try:
                    crawled_data = await self.crawler.crawl_website(url)
                    competitor_data.extend(crawled_data)
                    logger.info(f"경쟁사 URL 크롤링 완료: {url} ({len(crawled_data)}개 페이지)")
                except Exception as e:
                    logger.error(f"경쟁사 URL 크롤링 실패: {url}, 오류: {e}")
            
            # 2단계: 우리 제품 웹사이트 크롤링
            logger.info("우리 제품 웹사이트 크롤링 시작...")
            our_product_data = []
            for url in our_product_urls:
                try:
                    crawled_data = await self.crawler.crawl_website(url)
                    our_product_data.extend(crawled_data)
                    logger.info(f"우리 제품 URL 크롤링 완료: {url} ({len(crawled_data)}개 페이지)")
                except Exception as e:
                    logger.error(f"우리 제품 URL 크롤링 실패: {url}, 오류: {e}")
            
            # 3단계: Vertex AI를 사용한 기능 분석
            logger.info("Vertex AI 기능 분석 시작...")
            
            # 경쟁사 기능 분석
            competitor_features = await self._analyze_competitor_features(competitor_data)
            
            # 우리 제품 기능 분석
            our_product_features = await self._analyze_our_product_features(our_product_data)
            
            # 4단계: 기능 비교 분석
            logger.info("기능 비교 분석 시작...")
            comparison_analysis = await self._compare_features(
                competitor_features, 
                our_product_features
            )
            
            # 5단계: 결과 통합
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = {
                'project_info': {
                    'name': project_name,
                    'created_at': start_time.isoformat(),
                    'processing_time_seconds': processing_time,
                    'total_pages_crawled': len(competitor_data) + len(our_product_data)
                },
                'crawling_results': {
                    'competitor_pages': len(competitor_data),
                    'our_product_pages': len(our_product_data),
                    'competitor_urls': competitor_urls,
                    'our_product_urls': our_product_urls
                },
                'analysis_results': {
                    'competitor_features': competitor_features,
                    'our_product_features': our_product_features,
                    'comparison_analysis': comparison_analysis
                },
                'summary': {
                    'competitor_feature_count': len(competitor_features.get('extracted_features', [])),
                    'our_product_feature_count': len(our_product_features.get('extracted_features', [])),
                    'analysis_quality': self._assess_analysis_quality(competitor_data, our_product_data)
                }
            }
            
            logger.info(f"기능 탐지 완료: {project_name} (처리 시간: {processing_time:.2f}초)")
            return result
            
        except Exception as e:
            logger.error(f"기능 탐지 중 오류: {e}")
            return {
                'error': str(e),
                'success': False,
                'project_name': project_name
            }
    
    async def _analyze_competitor_features(self, competitor_data: List[Dict]) -> Dict[str, Any]:
        """경쟁사 데이터에서 기능 분석"""
        try:
            if not competitor_data:
                return {
                    'extracted_features': [],
                    'analysis_summary': {
                        'total_features': 0,
                        'main_categories': [],
                        'document_quality': 'low'
                    }
                }
            
            # 모든 페이지의 텍스트를 결합
            combined_text = self._combine_crawled_data(competitor_data)
            
            # Vertex AI로 기능 분석
            result = self.vertex_ai.extract_features_from_text("경쟁사", combined_text)
            
            logger.info(f"경쟁사 기능 분석 완료: {len(result.get('extracted_features', []))}개 기능")
            return result
            
        except Exception as e:
            logger.error(f"경쟁사 기능 분석 오류: {e}")
            return {
                'extracted_features': [],
                'analysis_summary': {
                    'total_features': 0,
                    'main_categories': [],
                    'document_quality': 'low',
                    'error': str(e)
                }
            }
    
    async def _analyze_our_product_features(self, our_product_data: List[Dict]) -> Dict[str, Any]:
        """우리 제품 데이터에서 기능 분석"""
        try:
            if not our_product_data:
                return {
                    'extracted_features': [],
                    'analysis_summary': {
                        'total_features': 0,
                        'main_categories': [],
                        'document_quality': 'low'
                    }
                }
            
            # 모든 페이지의 텍스트를 결합
            combined_text = self._combine_crawled_data(our_product_data)
            
            # Vertex AI로 기능 분석
            result = self.vertex_ai.extract_features_from_text("우리 제품", combined_text)
            
            logger.info(f"우리 제품 기능 분석 완료: {len(result.get('extracted_features', []))}개 기능")
            return result
            
        except Exception as e:
            logger.error(f"우리 제품 기능 분석 오류: {e}")
            return {
                'extracted_features': [],
                'analysis_summary': {
                    'total_features': 0,
                    'main_categories': [],
                    'document_quality': 'low',
                    'error': str(e)
                }
            }
    
    async def _compare_features(self, competitor_features: Dict, our_product_features: Dict) -> Dict[str, Any]:
        """두 제품의 기능을 비교 분석"""
        try:
            competitor_feature_list = competitor_features.get('extracted_features', [])
            our_product_feature_list = our_product_features.get('extracted_features', [])
            
            # Vertex AI로 기능 비교
            result = self.vertex_ai.compare_products(
                "경쟁사", competitor_feature_list,
                "우리 제품", our_product_feature_list
            )
            
            logger.info("기능 비교 분석 완료")
            return result
            
        except Exception as e:
            logger.error(f"기능 비교 분석 오류: {e}")
            return {
                'comparison_summary': {},
                'feature_comparison': [],
                'competitive_analysis': {
                    'error': str(e)
                }
            }
    
    def _combine_crawled_data(self, data: List[Dict]) -> str:
        """크롤링된 데이터를 하나의 텍스트로 결합"""
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
        
        return combined_text
    
    def _assess_analysis_quality(self, competitor_data: List[Dict], our_product_data: List[Dict]) -> str:
        """분석 품질 평가"""
        total_pages = len(competitor_data) + len(our_product_data)
        
        if total_pages >= 20:
            return "high"
        elif total_pages >= 10:
            return "medium"
        else:
            return "low"
    
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
