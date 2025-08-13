"""
AI 분석 API 라우트
"""

from flask import Blueprint, request, jsonify
from models.project import Project
from models.ai_analysis import AIAnalysis, ExtractedFeature, ProductComparison
from services.crawling_service import CrawlingService
from services.vertex_ai_service import VertexAIService
from tasks.ai_analysis_tasks import analyze_crawled_content_task, batch_ai_analysis_task
from extensions import db
import logging

logger = logging.getLogger(__name__)
ai_analysis_bp = Blueprint('ai_analysis', __name__)

@ai_analysis_bp.route('/projects/<int:project_id>/ai/analyze', methods=['POST'])
def analyze_crawled_content(project_id):
    """크롤링된 콘텐츠에 AI 분석 수행"""
    try:
        data = request.get_json()
        
        if not data or not data.get('crawling_result_id'):
            return jsonify({'error': '크롤링 결과 ID가 필요합니다.'}), 400
        
        crawling_result_id = data['crawling_result_id']
        
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 크롤링 서비스로 AI 분석 수행
        crawling_service = CrawlingService()
        
        # 크롤링 결과 조회
        from models.crawling_result import CrawlingResult
        crawling_result = CrawlingResult.query.get(crawling_result_id)
        if not crawling_result:
            return jsonify({'error': '크롤링 결과를 찾을 수 없습니다.'}), 404
        
        # AI 분석 수행
        crawl_data = {
            'url': crawling_result.url,
            'content': crawling_result.content
        }
        
        crawling_service._perform_ai_analysis(project_id, crawling_result_id, crawl_data)
        
        # 비동기 AI 분석 태스크 시작
        task = analyze_crawled_content_task.delay(project_id, crawling_result_id)
        
        return jsonify({
            'message': 'AI 분석이 시작되었습니다.',
            'task_id': task.id,
            'crawling_result_id': crawling_result_id
        }), 202
        
    except Exception as e:
        logger.error(f"AI 분석 중 오류: {e}")
        return jsonify({'error': 'AI 분석 중 오류가 발생했습니다.'}), 500

@ai_analysis_bp.route('/projects/<int:project_id>/ai/analyze/batch', methods=['POST'])
def batch_analyze_crawled_content(project_id):
    """여러 크롤링 결과에 배치 AI 분석 수행"""
    try:
        data = request.get_json()
        
        if not data or not data.get('crawling_result_ids'):
            return jsonify({'error': '크롤링 결과 ID 목록이 필요합니다.'}), 400
        
        crawling_result_ids = data['crawling_result_ids']
        
        if not isinstance(crawling_result_ids, list) or len(crawling_result_ids) == 0:
            return jsonify({'error': '유효한 크롤링 결과 ID 목록이 필요합니다.'}), 400
        
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 비동기 배치 AI 분석 태스크 시작
        task = batch_ai_analysis_task.delay(project_id, crawling_result_ids)
        
        return jsonify({
            'message': f'{len(crawling_result_ids)}개 결과에 대한 배치 AI 분석이 시작되었습니다.',
            'task_id': task.id,
            'crawling_result_ids': crawling_result_ids
        }), 202
        
    except Exception as e:
        logger.error(f"배치 AI 분석 중 오류: {e}")
        return jsonify({'error': '배치 AI 분석 중 오류가 발생했습니다.'}), 500

@ai_analysis_bp.route('/projects/<int:project_id>/ai/features', methods=['GET'])
def get_extracted_features(project_id):
    """추출된 기능 목록 조회"""
    try:
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 페이지네이션 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')  # 필터링
        
        # 쿼리 구성
        query = ExtractedFeature.query.join(AIAnalysis).filter(AIAnalysis.project_id == project_id)
        
        # 카테고리 필터링
        if category:
            query = query.filter(ExtractedFeature.category == category)
        
        # 페이지네이션
        features = query.order_by(ExtractedFeature.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'features': [feature.to_dict() for feature in features.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': features.total,
                'pages': features.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"기능 목록 조회 중 오류: {e}")
        return jsonify({'error': '기능 목록 조회 중 오류가 발생했습니다.'}), 500

@ai_analysis_bp.route('/projects/<int:project_id>/ai/features/summary', methods=['GET'])
def get_features_summary(project_id):
    """추출된 기능 요약 정보 조회"""
    try:
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 카테고리별 통계
        from sqlalchemy import func
        category_stats = db.session.query(
            ExtractedFeature.category,
            func.count(ExtractedFeature.id).label('count'),
            func.avg(ExtractedFeature.confidence_score).label('avg_confidence')
        ).join(AIAnalysis).filter(
            AIAnalysis.project_id == project_id
        ).group_by(ExtractedFeature.category).all()
        
        # 전체 통계
        total_features = ExtractedFeature.query.join(AIAnalysis).filter(
            AIAnalysis.project_id == project_id
        ).count()
        
        avg_confidence = db.session.query(
            func.avg(ExtractedFeature.confidence_score)
        ).join(AIAnalysis).filter(
            AIAnalysis.project_id == project_id
        ).scalar() or 0.0
        
        return jsonify({
            'total_features': total_features,
            'average_confidence': round(avg_confidence, 3),
            'category_stats': [
                {
                    'category': stat.category,
                    'count': stat.count,
                    'average_confidence': round(stat.avg_confidence, 3) if stat.avg_confidence else 0.0
                }
                for stat in category_stats
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"기능 요약 조회 중 오류: {e}")
        return jsonify({'error': '기능 요약 조회 중 오류가 발생했습니다.'}), 500

@ai_analysis_bp.route('/projects/<int:project_id>/ai/analyze-keyword', methods=['POST'])
def analyze_keyword_with_ai(project_id):
    """AI를 사용한 키워드 분석"""
    try:
        data = request.get_json()
        
        if not data or not data.get('keyword') or not data.get('content'):
            return jsonify({'error': '키워드와 콘텐츠가 필요합니다.'}), 400
        
        keyword = data['keyword']
        content = data['content']
        
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 크롤링 서비스로 AI 키워드 분석
        crawling_service = CrawlingService()
        result = crawling_service.analyze_keyword_with_ai(project_id, keyword, content)
        
        return jsonify({
            'keyword': keyword,
            'analysis_result': result
        }), 200
        
    except Exception as e:
        logger.error(f"AI 키워드 분석 중 오류: {e}")
        return jsonify({'error': 'AI 키워드 분석 중 오류가 발생했습니다.'}), 500

@ai_analysis_bp.route('/projects/<int:project_id>/ai/compare-products', methods=['POST'])
def compare_products_with_ai(project_id):
    """AI를 사용한 제품 비교 분석"""
    try:
        data = request.get_json()
        
        if not data or not data.get('product1') or not data.get('product2'):
            return jsonify({'error': '두 제품의 정보가 필요합니다.'}), 400
        
        product1 = data['product1']
        product2 = data['product2']
        
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 크롤링 서비스로 AI 제품 비교 분석
        crawling_service = CrawlingService()
        result = crawling_service.compare_products_with_ai(
            project_id,
            product1['name'], product1['features'],
            product2['name'], product2['features']
        )
        
        return jsonify({
            'comparison_result': result
        }), 200
        
    except Exception as e:
        logger.error(f"AI 제품 비교 분석 중 오류: {e}")
        return jsonify({'error': 'AI 제품 비교 분석 중 오류가 발생했습니다.'}), 500

@ai_analysis_bp.route('/projects/<int:project_id>/ai/comparisons', methods=['GET'])
def get_product_comparisons(project_id):
    """제품 비교 분석 결과 목록 조회"""
    try:
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 페이지네이션 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 제품 비교 결과 조회
        comparisons = ProductComparison.query.filter_by(
            project_id=project_id
        ).order_by(ProductComparison.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'comparisons': [comparison.to_dict() for comparison in comparisons.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': comparisons.total,
                'pages': comparisons.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"제품 비교 결과 조회 중 오류: {e}")
        return jsonify({'error': '제품 비교 결과 조회 중 오류가 발생했습니다.'}), 500

@ai_analysis_bp.route('/ai/status', methods=['GET'])
def get_ai_service_status():
    """AI 서비스 상태 확인"""
    try:
        # Vertex AI 서비스 상태 확인
        try:
            vertex_ai = VertexAIService()
            ai_status = {
                'vertex_ai': 'available',
                'project_id': vertex_ai.project_id,
                'model': vertex_ai.model
            }
        except Exception as e:
            ai_status = {
                'vertex_ai': 'unavailable',
                'error': str(e)
            }
        
        return jsonify({
            'ai_services': ai_status
        }), 200
        
    except Exception as e:
        logger.error(f"AI 서비스 상태 확인 중 오류: {e}")
        return jsonify({'error': 'AI 서비스 상태 확인 중 오류가 발생했습니다.'}), 500
