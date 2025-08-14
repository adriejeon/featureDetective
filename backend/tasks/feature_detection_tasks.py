#!/usr/bin/env python3
"""
기능 탐지 Celery 태스크 - 실시간 진행률 업데이트
"""

from celery import shared_task
from services.feature_detection_service import FeatureDetectionService
from models.job import Job
# 웹소켓 매니저는 함수 내에서 import (순환 참조 방지)
# from websocket_server import websocket_manager
from extensions import db
import logging
import asyncio

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def feature_detection_task(self, job_id: str, input_data: dict):
    """기능 탐지 태스크 - 실시간 진행률 업데이트"""
    try:
        logger.info(f"기능 탐지 태스크 시작: Job {job_id}")
        
        # Job 조회 및 상태 업데이트
        job = Job.query.get(job_id)
        if not job:
            raise Exception(f"Job을 찾을 수 없습니다: {job_id}")
        
        job.status = 'running'
        job.current_step = '초기화 중...'
        job.progress = 0
        db.session.commit()
        
        # 웹소켓으로 진행률 전송
        try:
            from websocket_server import websocket_manager
            websocket_manager.emit_job_progress(job_id, {
                'progress': 0,
                'current_step': '초기화 중...',
                'status': 'running'
            })
            logger.info(f"초기 진행률 전송 완료: Job {job_id}")
        except Exception as ws_error:
            logger.error(f"웹소켓 진행률 전송 실패: {ws_error}")
        
        # 입력 데이터 추출
        competitor_urls = input_data.get('competitor_urls', [])
        our_product_urls = input_data.get('our_product_urls', [])
        project_name = input_data.get('project_name', '기능 탐지 프로젝트')
        product_names = input_data.get('product_names', [])  # 제품명 목록 추가
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 5,
                'total': 100,
                'status': '서비스 초기화 중...'
            }
        )
        
        job.update_progress(5, '서비스 초기화 중...')
        try:
            from websocket_server import websocket_manager
            websocket_manager.emit_job_progress(job_id, {
                'progress': 5,
                'current_step': '서비스 초기화 중...',
                'status': 'running'
            })
            logger.info(f"서비스 초기화 진행률 전송 완료: Job {job_id}")
        except Exception as ws_error:
            logger.error(f"웹소켓 진행률 전송 실패: {ws_error}")
        
        # 기능 탐지 서비스 초기화
        feature_service = FeatureDetectionService()
        
        # 진행률 업데이트
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 10,
                'total': 100,
                'status': '크롤링 준비 중...'
            }
        )
        
        job.update_progress(10, '크롤링 준비 중...')
        websocket_manager.emit_job_progress(job_id, {
            'progress': 10,
            'current_step': '크롤링 준비 중...',
            'status': 'running'
        })
        
        # 1단계: 크롤링 (30%)
        logger.info("1단계: 웹사이트 크롤링 시작")
        job.update_progress(10, '웹사이트 크롤링 준비 중...')
        websocket_manager.emit_job_progress(job_id, {
            'progress': 10,
            'current_step': '웹사이트 크롤링 준비 중...',
            'status': 'running'
        })
        
        # 비동기 크롤링 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            all_urls = competitor_urls + our_product_urls
            total_urls = len(all_urls)
            
            # 제품명 처리
            if not product_names or len(product_names) < len(all_urls):
                # 제품명이 부족한 경우 기본값으로 채움
                for i in range(len(product_names) if product_names else 0, len(all_urls)):
                    product_names.append(f"제품{i+1}")
            
            all_product_data = {}
            for i, url in enumerate(all_urls):
                try:
                    # 개별 URL 크롤링 진행률 업데이트
                    crawl_progress = 10 + int((i / total_urls) * 30)
                    job.update_progress(crawl_progress, f'웹사이트 크롤링 중... ({i+1}/{total_urls})')
                    websocket_manager.emit_job_progress(job_id, {
                        'progress': crawl_progress,
                        'current_step': f'웹사이트 크롤링 중... ({i+1}/{total_urls})',
                        'status': 'running'
                    })
                    
                    crawled_data = loop.run_until_complete(
                        feature_service.crawler.crawl_website(url)
                    )
                    all_product_data[product_names[i]] = {
                        'url': url,
                        'data': crawled_data
                    }
                    logger.info(f"{product_names[i]} 크롤링 완료: {url}")
                    
                except Exception as e:
                    logger.error(f"{product_names[i]} 크롤링 실패: {url}, 오류: {e}")
                    all_product_data[product_names[i]] = {
                        'url': url,
                        'data': []
                    }
        finally:
            loop.close()
        
        # 2단계: 기능 분석 (40%)
        logger.info("2단계: Vertex AI 기능 분석 시작")
        job.update_progress(40, 'Vertex AI 기능 분석 준비 중...')
        websocket_manager.emit_job_progress(job_id, {
            'progress': 40,
            'current_step': 'Vertex AI 기능 분석 준비 중...',
            'status': 'running'
        })
        
        product_features = {}
        total_products = len(all_product_data)
        
        for i, (product_name, product_info) in enumerate(all_product_data.items()):
            if product_info['data']:
                # 개별 제품 분석 진행률 업데이트
                analysis_progress = 40 + int((i / total_products) * 40)
                job.update_progress(analysis_progress, f'Vertex AI 기능 분석 중... ({i+1}/{total_products})')
                websocket_manager.emit_job_progress(job_id, {
                    'progress': analysis_progress,
                    'current_step': f'Vertex AI 기능 분석 중... ({i+1}/{total_products})',
                    'status': 'running'
                })
                
                # Vertex AI 분석 서비스 사용
                features = loop.run_until_complete(
                    feature_service.vertex_ai_analysis._extract_features_from_data(
                        product_info['data'], 
                        product_name
                    )
                )
                product_features[product_name] = features
            else:
                product_features[product_name] = {
                    'extracted_features': [],
                    'analysis_summary': {
                        'total_features': 0,
                        'main_categories': [],
                        'document_quality': 'low'
                    }
                }
        
        # 3단계: 기능 병합 및 비교 (20%)
        logger.info("3단계: 기능 병합 및 비교 분석")
        job.update_progress(80, '기능 병합 및 비교 분석 중...')
        websocket_manager.emit_job_progress(job_id, {
            'progress': 80,
            'current_step': '기능 병합 및 비교 분석 중...',
            'status': 'running'
        })
        
        # 모든 기능 병합 및 중복 제거
        all_features = []
        for product_name, features in product_features.items():
            for feature in features.get('extracted_features', []):
                feature['product_name'] = product_name
                all_features.append(feature)
        
        # 중복 제거
        merged_features = feature_service.vertex_ai.merge_and_deduplicate_features(all_features)
        
        # 제품별 기능 매핑
        product_feature_mapping = feature_service._map_features_to_products(merged_features, product_features)
        
        # 4단계: 결과 정리 (5%)
        logger.info("4단계: 결과 정리")
        job.update_progress(90, '결과 정리 중...')
        websocket_manager.emit_job_progress(job_id, {
            'progress': 90,
            'current_step': '결과 정리 중...',
            'status': 'running'
        })
        
        # 최종 결과 구성
        from datetime import datetime
        start_time = datetime.now()
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # 프론트엔드 호환성을 위한 구조 변환
        product_names = list(product_features.keys())
        competitor_features = product_features.get(product_names[0] if len(product_names) > 0 else '제품1', {})
        our_product_features = product_features.get(product_names[1] if len(product_names) > 1 else '제품2', {})
        
        # 비교 분석 결과 생성
        comparison_analysis = feature_service._generate_comparison_analysis(
            competitor_features, our_product_features, merged_features, product_feature_mapping
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
                'comparison_analysis': comparison_analysis
            },
            'summary': {
                'total_unique_features': len(merged_features),
                'total_products_analyzed': len(all_urls),
                'analysis_quality': feature_service._assess_analysis_quality(all_product_data)
            }
        }
        
        # Job 완료
        job.mark_completed(result)
        
        # 웹소켓으로 완료 알림 전송
        websocket_manager.emit_job_completed(job_id, {
            'success': True,
            'data': result,
            'message': '기능 탐지가 완료되었습니다.'
        })
        
        logger.info(f"기능 탐지 태스크 완료: Job {job_id}")
        return result
        
    except Exception as e:
        logger.error(f"기능 탐지 태스크 실패: Job {job_id}, 오류: {e}")
        
        # Job 실패 처리
        if 'job' in locals():
            job.mark_failed(str(e))
            
            # 웹소켓으로 실패 알림 전송
            websocket_manager.emit_job_failed(job_id, {
                'success': False,
                'error': str(e),
                'message': '기능 탐지 중 오류가 발생했습니다.'
            })
        
        raise
