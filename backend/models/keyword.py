from datetime import datetime
from extensions import db

class Keyword(db.Model):
    """키워드 모델"""
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    keyword = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    feature_analyses = db.relationship('FeatureAnalysis', backref='keyword', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """키워드 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'keyword': self.keyword,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Keyword {self.keyword}>'
