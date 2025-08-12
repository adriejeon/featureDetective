from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

# 데이터베이스 초기화
db = SQLAlchemy()

# 모델 import
from models.project import Project
from models.keyword import Keyword
from models.crawling_result import CrawlingResult
from models.feature_analysis import FeatureAnalysis
from models.ai_analysis import AIAnalysis, ExtractedFeature, ProductComparison

def create_app(config_class=Config):
    """애플리케이션 팩토리 패턴"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 확장 초기화
    db.init_app(app)
    CORS(app, origins=['http://127.0.0.1:3000', 'http://localhost:3000'], supports_credentials=True)
    
    # 블루프린트 등록
    from routes.project_routes import project_bp
    from routes.keyword_routes import keyword_bp
    from routes.crawling_routes import crawling_bp
    from routes.report_routes import report_bp
    from routes.feature_analysis_routes import feature_analysis_bp
    from routes.auto_discovery_routes import auto_discovery_bp
    from routes.ai_analysis_routes import ai_analysis_bp
    from routes.advanced_crawling_routes import advanced_crawling_bp
    
    app.register_blueprint(project_bp, url_prefix='/api/projects')
    app.register_blueprint(keyword_bp, url_prefix='/api/keywords')
    app.register_blueprint(crawling_bp, url_prefix='/api/crawling')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(feature_analysis_bp, url_prefix='/api/feature-analysis')
    app.register_blueprint(auto_discovery_bp, url_prefix='/api/auto-discovery')
    app.register_blueprint(ai_analysis_bp, url_prefix='/api/ai')
    app.register_blueprint(advanced_crawling_bp)
    
    # 헬스체크 엔드포인트
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Feature Detective API is running'})
    
    # 에러 핸들러
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
