from flask import Blueprint, request, jsonify
from models.crawling_result import CrawlingResult, db
from models.project import Project
from services.crawling_service import CrawlingService
from tasks.crawling_tasks import crawl_urls_task

crawling_bp = Blueprint('crawling', __name__)

@crawling_bp.route('/projects/<int:project_id>/crawl', methods=['POST'])
def start_crawling(project_id):
    """크롤링 시작 API"""
    try:
        data = request.get_json()
        
        if not data or not data.get('urls'):
            return jsonify({'error': 'URL 목록이 필요합니다.'}), 400
        
        urls = data['urls']
        
        if not isinstance(urls, list) or len(urls) == 0:
            return jsonify({'error': '유효한 URL 목록이 필요합니다.'}), 400
        
        # 프로젝트 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 비동기 크롤링 태스크 시작
        task = crawl_urls_task.delay(project_id, urls)
        
        return jsonify({
            'message': '크롤링이 시작되었습니다.',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@crawling_bp.route('/projects/<int:project_id>/crawl/status', methods=['GET'])
def get_crawling_status(project_id):
    """크롤링 상태 조회 API"""
    try:
        # 최근 크롤링 결과 조회
        recent_results = CrawlingResult.query.filter_by(
            project_id=project_id
        ).order_by(CrawlingResult.crawled_at.desc()).limit(10).all()
        
        total_results = CrawlingResult.query.filter_by(project_id=project_id).count()
        
        return jsonify({
            'total_results': total_results,
            'recent_results': [result.to_dict() for result in recent_results]
        }), 200
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@crawling_bp.route('/projects/<int:project_id>/results', methods=['GET'])
def get_crawling_results(project_id):
    """크롤링 결과 목록 조회 API"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 페이지네이션
        results = CrawlingResult.query.filter_by(
            project_id=project_id
        ).order_by(CrawlingResult.crawled_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'results': [result.to_dict() for result in results.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': results.total,
                'pages': results.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@crawling_bp.route('/results/<int:result_id>', methods=['GET'])
def get_crawling_result(result_id):
    """특정 크롤링 결과 조회 API"""
    try:
        result = CrawlingResult.query.get(result_id)
        
        if not result:
            return jsonify({'error': '크롤링 결과를 찾을 수 없습니다.'}), 404
        
        return jsonify({
            'result': result.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@crawling_bp.route('/results/<int:result_id>', methods=['DELETE'])
def delete_crawling_result(result_id):
    """크롤링 결과 삭제 API"""
    try:
        result = CrawlingResult.query.get(result_id)
        
        if not result:
            return jsonify({'error': '크롤링 결과를 찾을 수 없습니다.'}), 404
        
        db.session.delete(result)
        db.session.commit()
        
        return jsonify({
            'message': '크롤링 결과가 삭제되었습니다.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500
