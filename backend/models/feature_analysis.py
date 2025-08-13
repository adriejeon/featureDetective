from datetime import datetime
from extensions import db

class FeatureAnalysis(db.Model):
    """기능 분석 결과 모델"""
    __tablename__ = 'feature_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    support_status = db.Column(db.String(10), nullable=False)  # O, X, △
    confidence_score = db.Column(db.Numeric(3, 2))  # 0.00 ~ 1.00
    matched_text = db.Column(db.Text)  # 매칭된 텍스트
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """기능 분석 결과를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'keyword_id': self.keyword_id,
            'url': self.url,
            'support_status': self.support_status,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'matched_text': self.matched_text,
            'analyzed_at': self.analyzed_at.isoformat()
        }
    
    def __repr__(self):
        return f'<FeatureAnalysis {self.keyword.keyword} - {self.support_status}>'
