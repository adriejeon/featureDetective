#!/usr/bin/env python3
"""
통합 기능 탐지 API 라우트
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import logging
from typing import List, Dict, Any
import asyncio

from services.feature_detection_service import FeatureDetectionService
from extensions import db

logger = logging.getLogger(__name__)

# Blueprint 생성
feature_detection_bp = Blueprint('feature_detection', __name__)

# 서비스 인스턴스 생성
feature_service = FeatureDetectionService()

@feature_detection_bp.route('/detect-features', methods=['POST'])
@cross_origin()
def detect_features():
    """
    URL 목록에서 기능 탐지 및 분석 (비동기 Job 시스템)
    
    요청 형식:
    {
        "competitor_urls": ["https://competitor1.com", "https://competitor2.com"],
        "our_product_urls": ["https://ourproduct.com"],
        "project_name": "프로젝트 이름"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        competitor_urls = data.get('competitor_urls', [])
        our_product_urls = data.get('our_product_urls', [])
        project_name = data.get('project_name', '기능 탐지 프로젝트')
        
        if not competitor_urls and not our_product_urls:
            return jsonify({'error': '최소 하나의 URL이 필요합니다.'}), 400
        
        logger.info(f"기능 탐지 Job 요청: {project_name}")
        logger.info(f"경쟁사 URL: {competitor_urls}")
        logger.info(f"우리 제품 URL: {our_product_urls}")
        
        # Job 생성
        from models.job import Job
        job = Job()
        job.project_id = 1  # 기본 프로젝트 ID (실제로는 사용자 프로젝트 사용)
        job.job_type = 'feature_detection'
        job.status = 'pending'
        job.progress = 0
        job.current_step = '대기 중'
        job.input_data = {
            'competitor_urls': competitor_urls,
            'our_product_urls': our_product_urls,
            'project_name': project_name
        }
        
        db.session.add(job)
        db.session.commit()
        
        # Celery 태스크 실행
        try:
            from tasks.feature_detection_tasks import feature_detection_task
            logger.info(f"Celery 태스크 시작: Job {job.id}")
            task = feature_detection_task.delay(job.id, job.input_data)
            logger.info(f"Celery 태스크 ID: {task.id}")
        except Exception as celery_error:
            logger.error(f"Celery 태스크 실행 오류: {celery_error}")
            # Celery 연결 실패 시 동기적으로 실행
            logger.info("Celery 연결 실패로 동기 실행으로 전환")
            from services.feature_detection_service import FeatureDetectionService
            feature_service = FeatureDetectionService()
            
            # 비동기 함수를 동기적으로 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    feature_service.detect_features_from_urls(
                        competitor_urls, 
                        our_product_urls, 
                        project_name
                    )
                )
            finally:
                loop.close()
            
            # Job 완료로 표시
            job.status = 'completed'
            job.progress = 100
            job.current_step = '완료'
            job.result_data = result
            db.session.commit()
            
            # 웹소켓으로 완료 알림 전송
            try:
                from websocket_server import websocket_manager
                websocket_manager.emit_job_completed(job.id, {
                    'success': True,
                    'data': result,
                    'message': '기능 탐지가 완료되었습니다.'
                })
                logger.info(f"웹소켓 완료 알림 전송: Job {job.id}")
            except Exception as ws_error:
                logger.error(f"웹소켓 알림 전송 실패: {ws_error}")
            
            return jsonify({
                'success': True,
                'message': '기능 탐지가 완료되었습니다.',
                'data': result
            }), 200
        
        # Job에 Celery 태스크 ID 저장
        job.celery_task_id = task.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '기능 탐지가 시작되었습니다.',
            'data': {
                'job_id': job.id,
                'status': job.status,
                'progress': job.progress,
                'current_step': job.current_step
            }
        }), 202
        
    except Exception as e:
        logger.error(f"기능 탐지 Job 생성 오류: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@feature_detection_bp.route('/analyze-single-url', methods=['POST'])
@cross_origin()
def analyze_single_url():
    """
    단일 URL에서 기능 분석
    
    요청 형식:
    {
        "url": "https://example.com",
        "company_name": "회사명"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        url = data.get('url')
        company_name = data.get('company_name', '분석 대상')
        
        if not url:
            return jsonify({'error': 'URL이 필요합니다.'}), 400
        
        logger.info(f"단일 URL 분석 요청: {url}")
        
        # 비동기 함수 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                feature_service.analyze_single_url(url, company_name)
            )
        finally:
            loop.close()
        
        if result.get('error'):
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"단일 URL 분석 API 오류: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@feature_detection_bp.route('/analyze-keyword-support', methods=['POST'])
@cross_origin()
def analyze_keyword_support():
    """
    특정 URL에서 키워드 지원 여부 분석
    
    요청 형식:
    {
        "url": "https://example.com",
        "keyword": "분석할 키워드"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        url = data.get('url')
        keyword = data.get('keyword')
        
        if not url or not keyword:
            return jsonify({'error': 'URL과 키워드가 모두 필요합니다.'}), 400
        
        logger.info(f"키워드 지원 분석 요청: {url} - {keyword}")
        
        # 비동기 함수 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                feature_service.analyze_keyword_support(url, keyword)
            )
        finally:
            loop.close()
        
        if result.get('error'):
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"키워드 지원 분석 API 오류: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@feature_detection_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """서비스 상태 확인"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'feature_detection',
            'vertex_ai_available': feature_service.vertex_ai.client is not None
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@feature_detection_bp.route('/test-vertex-ai', methods=['POST'])
@cross_origin()
def test_vertex_ai():
    """
    Vertex AI 연결 테스트
    
    요청 형식:
    {
        "test_text": "테스트할 텍스트"
    }
    """
    try:
        data = request.get_json()
        test_text = data.get('test_text', '안녕하세요. 이것은 테스트입니다.')
        
        logger.info("Vertex AI 연결 테스트 시작")
        
        # 간단한 기능 추출 테스트
        result = feature_service.vertex_ai.extract_features_from_text("테스트", test_text)
        
        return jsonify({
            'success': True,
            'vertex_ai_working': True,
            'test_result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Vertex AI 테스트 오류: {e}")
        return jsonify({
            'success': False,
            'vertex_ai_working': False,
            'error': str(e)
        }), 500
