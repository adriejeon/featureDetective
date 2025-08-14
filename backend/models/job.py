"""
Job 상태 관리 모델
"""

from datetime import datetime
from extensions import db
import json
import uuid

class Job(db.Model):
    """분석 Job 모델"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)  # feature_detection, ai_analysis, crawling
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, running, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    current_step = db.Column(db.String(100))  # 현재 진행 중인 단계
    input_data = db.Column(db.JSON)  # 입력 데이터
    result_data = db.Column(db.JSON)  # 결과 데이터
    error_message = db.Column(db.Text)  # 오류 메시지
    celery_task_id = db.Column(db.String(255))  # Celery 태스크 ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # 관계 설정
    project = db.relationship('Project', backref='jobs')
    
    def to_dict(self):
        """Job을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'job_type': self.job_type,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'input_data': self.input_data,
            'result_data': self.result_data,
            'error_message': self.error_message,
            'celery_task_id': self.celery_task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def update_progress(self, progress: int, current_step: str = None):
        """진행률 업데이트"""
        self.progress = progress
        if current_step:
            self.current_step = current_step
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def mark_completed(self, result_data: dict = None):
        """완료 상태로 변경"""
        self.status = 'completed'
        self.progress = 100
        self.current_step = '완료'
        if result_data:
            self.result_data = result_data
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def mark_failed(self, error_message: str):
        """실패 상태로 변경"""
        self.status = 'failed'
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<Job {self.id} - {self.job_type} ({self.status})>'

