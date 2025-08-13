"""
AI 분석 결과 모델
"""

from datetime import datetime
from extensions import db
import json

class AIAnalysis(db.Model):
    """AI 분석 결과 모델"""
    __tablename__ = 'ai_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    crawling_result_id = db.Column(db.Integer, db.ForeignKey('crawling_results.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # feature_extraction, keyword_analysis, product_comparison
    analysis_data = db.Column(db.JSON)  # AI 분석 결과 데이터
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    project = db.relationship('Project', backref='ai_analyses')
    crawling_result = db.relationship('CrawlingResult', backref='ai_analyses')
    
    def to_dict(self):
        """AI 분석 결과를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'crawling_result_id': self.crawling_result_id,
            'analysis_type': self.analysis_type,
            'analysis_data': self.analysis_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AIAnalysis {self.analysis_type} for project {self.project_id}>'


class ExtractedFeature(db.Model):
    """추출된 기능 모델"""
    __tablename__ = 'extracted_features'
    
    id = db.Column(db.Integer, primary_key=True)
    ai_analysis_id = db.Column(db.Integer, db.ForeignKey('ai_analyses.id'), nullable=False)
    feature_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # UI_UX, 보안, 통합, 성능, 관리, 기타
    description = db.Column(db.Text)
    confidence_score = db.Column(db.Float)  # 0.0-1.0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    ai_analysis = db.relationship('AIAnalysis', backref='extracted_features')
    
    def to_dict(self):
        """추출된 기능을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'ai_analysis_id': self.ai_analysis_id,
            'feature_name': self.feature_name,
            'category': self.category,
            'description': self.description,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ExtractedFeature {self.feature_name}>'


class ProductComparison(db.Model):
    """제품 비교 분석 모델"""
    __tablename__ = 'product_comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    product1_name = db.Column(db.String(200), nullable=False)
    product2_name = db.Column(db.String(200), nullable=False)
    comparison_data = db.Column(db.JSON)  # 비교 분석 결과 데이터
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    project = db.relationship('Project', backref='product_comparisons')
    
    def to_dict(self):
        """제품 비교 분석을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'product1_name': self.product1_name,
            'product2_name': self.product2_name,
            'comparison_data': self.comparison_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ProductComparison {self.product1_name} vs {self.product2_name}>'
