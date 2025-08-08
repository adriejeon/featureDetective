from flask import Blueprint, request, jsonify
from models.project import Project, db

project_bp = Blueprint('project', __name__)

@project_bp.route('/', methods=['OPTIONS'])
def handle_options():
    """CORS preflight 요청 처리"""
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

@project_bp.route('/', methods=['GET'])
def get_projects():
    """프로젝트 목록 조회 API"""
    try:
        projects = Project.query.all()
        return jsonify({
            'projects': [project.to_dict() for project in projects]
        }), 200
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@project_bp.route('/', methods=['POST'])
def create_project():
    """새 프로젝트 생성 API"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': '프로젝트 이름이 필요합니다.'}), 400
        
        name = data['name']
        description = data.get('description', '')
        
        # 새 프로젝트 생성
        new_project = Project()
        new_project.name = name
        new_project.description = description
        new_project.user_id = 1  # 기본 사용자 ID
        
        db.session.add(new_project)
        db.session.commit()
        
        return jsonify({
            'message': '프로젝트가 생성되었습니다.',
            'project': new_project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@project_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """특정 프로젝트 조회 API"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        return jsonify({
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@project_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """프로젝트 수정 API"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        data = request.get_json()
        
        if data.get('name'):
            project.name = data['name']
        if data.get('description') is not None:
            project.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': '프로젝트가 수정되었습니다.',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@project_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """프로젝트 삭제 API"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'message': '프로젝트가 삭제되었습니다.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500
