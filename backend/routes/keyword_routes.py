from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.keyword import Keyword, db
from models.project import Project
import csv
import io

keyword_bp = Blueprint('keyword', __name__)

@keyword_bp.route('/projects/<int:project_id>/keywords', methods=['GET'])
@login_required
def get_keywords(project_id):
    """프로젝트의 키워드 목록 조회 API"""
    try:
        # 프로젝트 권한 확인
        project = Project.query.filter_by(
            id=project_id, 
            user_id=current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        return jsonify({
            'keywords': [keyword.to_dict() for keyword in keywords]
        }), 200
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@keyword_bp.route('/projects/<int:project_id>/keywords', methods=['POST'])
@login_required
def create_keyword(project_id):
    """새 키워드 생성 API"""
    try:
        # 프로젝트 권한 확인
        project = Project.query.filter_by(
            id=project_id, 
            user_id=current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('keyword'):
            return jsonify({'error': '키워드가 필요합니다.'}), 400
        
        keyword_text = data['keyword']
        category = data.get('category', '')
        
        # 새 키워드 생성
        new_keyword = Keyword()
        new_keyword.keyword = keyword_text
        new_keyword.category = category
        new_keyword.project_id = project_id
        
        db.session.add(new_keyword)
        db.session.commit()
        
        return jsonify({
            'message': '키워드가 생성되었습니다.',
            'keyword': new_keyword.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@keyword_bp.route('/keywords/<int:keyword_id>', methods=['PUT'])
@login_required
def update_keyword(keyword_id):
    """키워드 수정 API"""
    try:
        keyword = Keyword.query.join(Project).filter(
            Keyword.id == keyword_id,
            Project.user_id == current_user.id
        ).first()
        
        if not keyword:
            return jsonify({'error': '키워드를 찾을 수 없습니다.'}), 404
        
        data = request.get_json()
        
        if data.get('keyword'):
            keyword.keyword = data['keyword']
        if data.get('category') is not None:
            keyword.category = data['category']
        
        db.session.commit()
        
        return jsonify({
            'message': '키워드가 수정되었습니다.',
            'keyword': keyword.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@keyword_bp.route('/keywords/<int:keyword_id>', methods=['DELETE'])
@login_required
def delete_keyword(keyword_id):
    """키워드 삭제 API"""
    try:
        keyword = Keyword.query.join(Project).filter(
            Keyword.id == keyword_id,
            Project.user_id == current_user.id
        ).first()
        
        if not keyword:
            return jsonify({'error': '키워드를 찾을 수 없습니다.'}), 404
        
        db.session.delete(keyword)
        db.session.commit()
        
        return jsonify({
            'message': '키워드가 삭제되었습니다.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@keyword_bp.route('/projects/<int:project_id>/keywords/upload', methods=['POST'])
@login_required
def upload_keywords_csv(project_id):
    """CSV 파일로 키워드 업로드 API"""
    try:
        # 프로젝트 권한 확인
        project = Project.query.filter_by(
            id=project_id, 
            user_id=current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': '파일이 필요합니다.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'CSV 파일만 업로드 가능합니다.'}), 400
        
        # CSV 파일 읽기
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        created_count = 0
        for row in csv_reader:
            keyword_text = row.get('keyword', '').strip()
            category = row.get('category', '').strip()
            
            if keyword_text:
                # 중복 키워드 확인
                existing = Keyword.query.filter_by(
                    project_id=project_id,
                    keyword=keyword_text
                ).first()
                
                if not existing:
                    new_keyword = Keyword()
                    new_keyword.keyword = keyword_text
                    new_keyword.category = category
                    new_keyword.project_id = project_id
                    db.session.add(new_keyword)
                    created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'{created_count}개의 키워드가 업로드되었습니다.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@keyword_bp.route('/projects/<int:project_id>/keywords/download', methods=['GET'])
@login_required
def download_keywords_csv(project_id):
    """키워드 목록을 CSV로 다운로드 API"""
    try:
        # 프로젝트 권한 확인
        project = Project.query.filter_by(
            id=project_id, 
            user_id=current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        
        # CSV 생성
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['keyword', 'category'])
        
        for keyword in keywords:
            writer.writerow([keyword.keyword, keyword.category or ''])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=keywords_{project_id}.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500
