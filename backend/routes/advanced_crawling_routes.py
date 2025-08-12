"""
고급 크롤링 API 라우트
Intercom과 같은 고급 크롤링 기능을 제공하는 API 엔드포인트
"""

from flask import Blueprint, request, jsonify
from services.advanced_crawling_service import AdvancedCrawlingService
from models.project import Project
from models.crawling_result import CrawlingResult
import logging
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)

# Blueprint 생성
advanced_crawling_bp = Blueprint('advanced_crawling', __name__, url_prefix='/api/advanced-crawling')

# 서비스 초기화
crawling_service = AdvancedCrawlingService()


@advanced_crawling_bp.route('/crawl-site', methods=['POST'])
def crawl_site_advanced():
    """
    고급 사이트 크롤링 API
    
    Request Body:
    {
        "project_id": 1,
        "base_url": "https://example.com",
        "config": {
            "max_pages": 50,
            "max_depth": 3,
            "include_patterns": ["*/help/*", "*/docs/*"],
            "exclude_patterns": ["*.pdf", "*.zip"],
            "css_exclude_selectors": ["nav", "footer"]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        project_id = data.get('project_id')
        base_url = data.get('base_url')
        
        if not project_id or not base_url:
            return jsonify({'error': 'project_id와 base_url은 필수입니다.'}), 400
        
        # 프로젝트 존재 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 설정 파싱
        config_data = data.get('config', {})
        config = None
        if config_data:
            config = crawling_service.create_custom_config(**config_data)
        
        # 크롤링 실행
        results = crawling_service.crawl_site_advanced(base_url, project_id, config)
        
        # 결과 요약
        summary = {
            'project_id': project_id,
            'base_url': base_url,
            'total_pages': len(results),
            'successful_pages': len([r for r in results if r.status == 'completed']),
            'failed_pages': len([r for r in results if r.status == 'failed']),
            'results': [
                {
                    'id': r.id,
                    'url': r.url,
                    'title': r.metadata.get('title', '') if r.metadata else '',
                    'status': r.status,
                    'content_length': r.content_length,
                    'extraction_method': r.extraction_method
                }
                for r in results
            ]
        }
        
        return jsonify({
            'success': True,
            'message': '고급 크롤링이 완료되었습니다.',
            'data': summary
        }), 200
        
    except Exception as e:
        logger.error(f"고급 크롤링 API 오류: {e}")
        return jsonify({
            'error': f'크롤링 중 오류가 발생했습니다: {str(e)}'
        }), 500


@advanced_crawling_bp.route('/crawl-help-center', methods=['POST'])
def crawl_help_center():
    """
    헬프 센터 전용 크롤링 API
    
    Request Body:
    {
        "project_id": 1,
        "base_url": "https://example.com/help"
    }
    """
    try:
        logger.info("=== 헬프 센터 크롤링 요청 시작 ===")
        logger.info(f"요청 헤더: {dict(request.headers)}")
        logger.info(f"요청 메서드: {request.method}")
        logger.info(f"요청 URL: {request.url}")
        logger.info(f"요청 Content-Type: {request.content_type}")
        
        data = request.get_json()
        logger.info(f"헬프 센터 크롤링 요청 데이터: {data}")
        logger.info(f"요청 데이터 타입: {type(data)}")
        
        if not data:
            logger.error("요청 데이터가 없습니다.")
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        project_id = data.get('project_id')
        base_url = data.get('base_url')
        
        logger.info(f"project_id: {project_id} (타입: {type(project_id)})")
        logger.info(f"base_url: {base_url} (타입: {type(base_url)})")
        
        if not project_id or not base_url:
            logger.error(f"필수 필드 누락 - project_id: {project_id}, base_url: {base_url}")
            return jsonify({'error': 'project_id와 base_url은 필수입니다.'}), 400
        
        # 프로젝트 존재 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 헬프 센터 크롤링 실행
        results = crawling_service.crawl_help_center(base_url, project_id)
        
        summary = {
            'project_id': project_id,
            'base_url': base_url,
            'crawl_type': 'help_center',
            'total_pages': len(results),
            'successful_pages': len([r for r in results if r.status == 'completed']),
            'failed_pages': len([r for r in results if r.status == 'failed'])
        }
        
        return jsonify({
            'success': True,
            'message': '헬프 센터 크롤링이 완료되었습니다.',
            'data': summary
        }), 200
        
    except Exception as e:
        logger.error(f"헬프 센터 크롤링 API 오류: {e}")
        return jsonify({
            'error': f'크롤링 중 오류가 발생했습니다: {str(e)}'
        }), 500


@advanced_crawling_bp.route('/crawl-documentation', methods=['POST'])
def crawl_documentation():
    """
    문서 사이트 전용 크롤링 API
    
    Request Body:
    {
        "project_id": 1,
        "base_url": "https://example.com/docs"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        project_id = data.get('project_id')
        base_url = data.get('base_url')
        
        if not project_id or not base_url:
            return jsonify({'error': 'project_id와 base_url은 필수입니다.'}), 400
        
        # 프로젝트 존재 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 문서 사이트 크롤링 실행
        results = crawling_service.crawl_documentation(base_url, project_id)
        
        summary = {
            'project_id': project_id,
            'base_url': base_url,
            'crawl_type': 'documentation',
            'total_pages': len(results),
            'successful_pages': len([r for r in results if r.status == 'completed']),
            'failed_pages': len([r for r in results if r.status == 'failed'])
        }
        
        return jsonify({
            'success': True,
            'message': '문서 사이트 크롤링이 완료되었습니다.',
            'data': summary
        }), 200
        
    except Exception as e:
        logger.error(f"문서 사이트 크롤링 API 오류: {e}")
        return jsonify({
            'error': f'크롤링 중 오류가 발생했습니다: {str(e)}'
        }), 500


@advanced_crawling_bp.route('/crawl-custom', methods=['POST'])
def crawl_with_custom_settings():
    """
    사용자 정의 설정으로 크롤링 API
    
    Request Body:
    {
        "project_id": 1,
        "base_url": "https://example.com",
        "include_patterns": ["*/help/*", "*/docs/*"],
        "exclude_patterns": ["*.pdf", "*.zip"],
        "css_exclude_selectors": ["nav", "footer"],
        "max_pages": 50,
        "max_depth": 3
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        project_id = data.get('project_id')
        base_url = data.get('base_url')
        
        if not project_id or not base_url:
            return jsonify({'error': 'project_id와 base_url은 필수입니다.'}), 400
        
        # 프로젝트 존재 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 사용자 정의 설정으로 크롤링
        results = crawling_service.crawl_with_custom_settings(
            base_url=base_url,
            project_id=project_id,
            include_patterns=data.get('include_patterns'),
            exclude_patterns=data.get('exclude_patterns'),
            css_exclude_selectors=data.get('css_exclude_selectors'),
            max_pages=data.get('max_pages', 50),
            max_depth=data.get('max_depth', 3)
        )
        
        summary = {
            'project_id': project_id,
            'base_url': base_url,
            'crawl_type': 'custom',
            'total_pages': len(results),
            'successful_pages': len([r for r in results if r.status == 'completed']),
            'failed_pages': len([r for r in results if r.status == 'failed']),
            'settings': {
                'include_patterns': data.get('include_patterns'),
                'exclude_patterns': data.get('exclude_patterns'),
                'css_exclude_selectors': data.get('css_exclude_selectors'),
                'max_pages': data.get('max_pages', 50),
                'max_depth': data.get('max_depth', 3)
            }
        }
        
        return jsonify({
            'success': True,
            'message': '사용자 정의 크롤링이 완료되었습니다.',
            'data': summary
        }), 200
        
    except Exception as e:
        logger.error(f"사용자 정의 크롤링 API 오류: {e}")
        return jsonify({
            'error': f'크롤링 중 오류가 발생했습니다: {str(e)}'
        }), 500


@advanced_crawling_bp.route('/status/<int:project_id>', methods=['GET'])
def get_crawling_status(project_id: int):
    """
    크롤링 상태 조회 API
    
    Args:
        project_id: 프로젝트 ID
    """
    try:
        # 프로젝트 존재 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 크롤링 상태 조회
        status_summary, results = crawling_service.get_crawling_status(project_id)
        
        # 결과 상세 정보
        detailed_results = []
        for result in results:
            # metadata가 JSON인지 확인하고 안전하게 처리
            title = ''
            if result.crawling_metadata:
                if isinstance(result.crawling_metadata, dict):
                    title = result.crawling_metadata.get('title', '')
                else:
                    # JSON 문자열인 경우 파싱
                    try:
                        import json
                        metadata_dict = json.loads(result.crawling_metadata)
                        title = metadata_dict.get('title', '')
                    except:
                        title = ''
            
            detailed_results.append({
                'id': result.id,
                'url': result.url,
                'title': title,
                'status': result.status,
                'content_length': result.content_length,
                'extraction_method': result.extraction_method,
                'created_at': result.crawled_at.isoformat() if result.crawled_at else None,
                'error_message': result.error_message
            })
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'status_summary': status_summary,
                'results': detailed_results
            }
        }), 200
        
    except Exception as e:
        logger.error(f"크롤링 상태 조회 API 오류: {e}")
        return jsonify({
            'error': f'상태 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@advanced_crawling_bp.route('/export/<int:project_id>', methods=['POST'])
def export_crawl_results(project_id: int):
    """
    크롤링 결과 내보내기 API
    
    Request Body:
    {
        "format": "json",  // "json" 또는 "csv"
        "filepath": "/path/to/export/file.json"
    }
    """
    try:
        data = request.get_json() or {}
        
        # 프로젝트 존재 확인
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        format_type = data.get('format', 'json')
        filepath = data.get('filepath', f'crawl_results_{project_id}.{format_type}')
        
        if format_type not in ['json', 'csv']:
            return jsonify({'error': '지원하지 않는 형식입니다. json 또는 csv를 사용하세요.'}), 400
        
        # 결과 내보내기
        crawling_service.export_crawl_results(project_id, filepath, format_type)
        
        return jsonify({
            'success': True,
            'message': '크롤링 결과가 성공적으로 내보내졌습니다.',
            'data': {
                'project_id': project_id,
                'filepath': filepath,
                'format': format_type
            }
        }), 200
        
    except Exception as e:
        logger.error(f"크롤링 결과 내보내기 API 오류: {e}")
        return jsonify({
            'error': f'내보내기 중 오류가 발생했습니다: {str(e)}'
        }), 500


@advanced_crawling_bp.route('/config/templates', methods=['GET'])
def get_config_templates():
    """
    크롤링 설정 템플릿 조회 API
    """
    templates = {
        'help_center': {
            'name': '헬프 센터',
            'description': '헬프 센터 사이트에 최적화된 설정',
            'max_pages': 100,
            'max_depth': 4,
            'include_patterns': [
                '*/help/*', '*/support/*', '*/docs/*', '*/guide/*',
                '*/manual/*', '*/tutorial/*', '*/faq/*', '*/knowledge/*'
            ],
            'exclude_patterns': [
                '*.pdf', '*.doc', '*.docx', '*.zip', '*.rar',
                'mailto:', 'tel:', 'javascript:',
                '/admin/', '/login/', '/logout/', '/register/',
                '?utm_', '?fbclid', '?gclid'
            ],
            'css_exclude_selectors': [
                'nav', 'footer', 'header', 'aside', 'sidebar',
                '.advertisement', '.ads', '.banner', '.popup',
                '.cookie-notice', '.newsletter', '.social-share',
                'script', 'style', 'noscript'
            ]
        },
        'documentation': {
            'name': '문서 사이트',
            'description': 'API 문서 및 기술 문서 사이트에 최적화된 설정',
            'max_pages': 200,
            'max_depth': 5,
            'include_patterns': [
                '*/docs/*', '*/documentation/*', '*/api/*', '*/reference/*',
                '*/guide/*', '*/tutorial/*', '*/examples/*', '*/getting-started/*'
            ],
            'exclude_patterns': [
                '*.pdf', '*.zip', '*.tar.gz',
                'mailto:', 'tel:', 'javascript:',
                '/admin/', '/login/', '/logout/',
                '?utm_', '?fbclid', '?gclid'
            ],
            'css_exclude_selectors': [
                'nav', 'footer', 'header', 'aside', 'sidebar',
                '.advertisement', '.ads', '.banner', '.popup',
                '.cookie-notice', '.newsletter', '.social-share',
                'script', 'style', 'noscript'
            ]
        },
        'ecommerce': {
            'name': '이커머스 사이트',
            'description': '온라인 쇼핑몰에 최적화된 설정',
            'max_pages': 150,
            'max_depth': 4,
            'include_patterns': [
                '*/product/*', '*/category/*', '*/shop/*',
                '*/help/*', '*/support/*', '*/faq/*'
            ],
            'exclude_patterns': [
                '*.pdf', '*.zip', '*.rar',
                'mailto:', 'tel:', 'javascript:',
                '/cart/', '/checkout/', '/login/', '/register/',
                '?utm_', '?fbclid', '?gclid'
            ],
            'css_exclude_selectors': [
                'nav', 'footer', 'header', 'aside', 'sidebar',
                '.advertisement', '.ads', '.banner', '.popup',
                '.cookie-notice', '.newsletter', '.social-share',
                'script', 'style', 'noscript'
            ]
        }
    }
    
    return jsonify({
        'success': True,
        'data': templates
    }), 200
