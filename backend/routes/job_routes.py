#!/usr/bin/env python3
"""
Job 관리 API 라우트
"""

from flask import Blueprint, request, jsonify
from models.job import Job
from models.project import Project
from extensions import db
import logging

logger = logging.getLogger(__name__)
job_bp = Blueprint('job', __name__)

@job_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Job 상태 조회"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job을 찾을 수 없습니다.'}), 404
        
        return jsonify({
            'success': True,
            'data': job.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Job 상태 조회 중 오류: {e}")
        return jsonify({'error': 'Job 상태 조회 중 오류가 발생했습니다.'}), 500

@job_bp.route('/projects/<int:project_id>/jobs', methods=['GET'])
def get_project_jobs(project_id):
    """프로젝트의 모든 Job 조회"""
    try:
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # Job 목록 조회
        jobs = Job.query.filter_by(project_id=project_id).order_by(Job.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [job.to_dict() for job in jobs]
        }), 200
        
    except Exception as e:
        logger.error(f"프로젝트 Job 조회 중 오류: {e}")
        return jsonify({'error': '프로젝트 Job 조회 중 오류가 발생했습니다.'}), 500

@job_bp.route('/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Job 취소"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job을 찾을 수 없습니다.'}), 404
        
        if job.status in ['completed', 'failed']:
            return jsonify({'error': '이미 완료되거나 실패한 Job입니다.'}), 400
        
        # Celery 태스크 취소 (있는 경우)
        if job.celery_task_id:
            from celery.result import AsyncResult
            task_result = AsyncResult(job.celery_task_id)
            task_result.revoke(terminate=True)
        
        # Job 상태를 취소로 변경
        job.status = 'cancelled'
        job.current_step = '취소됨'
        job.updated_at = db.func.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job이 취소되었습니다.',
            'data': job.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Job 취소 중 오류: {e}")
        return jsonify({'error': 'Job 취소 중 오류가 발생했습니다.'}), 500

@job_bp.route('/jobs/<job_id>/retry', methods=['POST'])
def retry_job(job_id):
    """실패한 Job 재시도"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job을 찾을 수 없습니다.'}), 404
        
        if job.status != 'failed':
            return jsonify({'error': '실패한 Job만 재시도할 수 있습니다.'}), 400
        
        # 새로운 Job 생성 (기존 입력 데이터 사용)
        new_job = Job()
        new_job.project_id = job.project_id
        new_job.job_type = job.job_type
        new_job.input_data = job.input_data
        new_job.status = 'pending'
        new_job.progress = 0
        new_job.current_step = '대기 중'
        
        db.session.add(new_job)
        db.session.commit()
        
        # 해당 Job 타입에 맞는 태스크 실행
        if job.job_type == 'feature_detection':
            from tasks.feature_detection_tasks import feature_detection_task
            task = feature_detection_task.delay(new_job.id, job.input_data)
            new_job.celery_task_id = task.id
        elif job.job_type == 'ai_analysis':
            from tasks.ai_analysis_tasks import analyze_crawled_content_task
            task = analyze_crawled_content_task.delay(
                job.input_data.get('project_id'), 
                job.input_data.get('crawling_result_id')
            )
            new_job.celery_task_id = task.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job이 재시도되었습니다.',
            'data': new_job.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Job 재시도 중 오류: {e}")
        return jsonify({'error': 'Job 재시도 중 오류가 발생했습니다.'}), 500

