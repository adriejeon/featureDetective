from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

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
    
    def to_dict(self):
        """크롤링 결과를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'url': self.url,
            'content': self.content[:500] + '...' if self.content and len(self.content) > 500 else self.content,
            'status': self.status,
            'error_message': self.error_message,
            'crawled_at': self.crawled_at.isoformat()
        }
    
    def __repr__(self):
        return f'<CrawlingResult {self.url}>'
