from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Project(db.Model):
    """프로젝트 모델"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False, default=1)  # 기본 사용자 ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    keywords = db.relationship('Keyword', backref='project', lazy=True, cascade='all, delete-orphan')
    crawling_results = db.relationship('CrawlingResult', backref='project', lazy=True, cascade='all, delete-orphan')
    feature_analyses = db.relationship('FeatureAnalysis', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """프로젝트 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'keyword_count': len(self.keywords),
            'crawling_count': len(self.crawling_results)
        }
    
    def __repr__(self):
        return f'<Project {self.name}>'
