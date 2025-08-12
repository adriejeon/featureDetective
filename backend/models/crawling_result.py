from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db
import json

class CrawlingResult(db.Model):
    """크롤링 결과 모델"""
    __tablename__ = 'crawling_results'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text)
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow)
    crawling_metadata = db.Column(db.JSON)  # 크롤링 메타데이터 (제목, 헤딩, 링크 등)
    content_length = db.Column(db.Integer)  # 콘텐츠 길이
    extraction_method = db.Column(db.String(50))  # 추출 방법 (main_content, readability)
    
    def to_dict(self):
        """크롤링 결과를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'url': self.url,
            'content': self.content[:500] + '...' if self.content and len(self.content) > 500 else self.content,
            'status': self.status,
            'error_message': self.error_message,
            'crawled_at': self.crawled_at.isoformat() if self.crawled_at else None,
            'metadata': self.crawling_metadata,
            'content_length': self.content_length,
            'extraction_method': self.extraction_method
        }
    
    def __repr__(self):
        return f'<CrawlingResult {self.url}>'
