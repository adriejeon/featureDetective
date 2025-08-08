from flask import Blueprint, request, jsonify
from models.keyword import Keyword, db
from models.project import Project
import csv
import io

keyword_bp = Blueprint('keyword', __name__)

@keyword_bp.route('/projects/<int:project_id>/keywords', methods=['GET'])
def get_keywords(project_id):
    """프로젝트의 키워드 목록 조회 API"""
    try:
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        return jsonify({
            'keywords': [keyword.to_dict() for keyword in keywords]
        }), 200
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@keyword_bp.route('/projects/<int:project_id>/keywords', methods=['POST'])
def create_keyword(project_id):
    """새 키워드 생성 API"""
    try:
        data = request.get_json()
        
        if not data or not data.get('keyword'):
            return jsonify({'error': '키워드가 필요합니다.'}), 400
        
        keyword_text = data['keyword']
        category = data.get('category', '기타')
        
        # 새 키워드 생성
        new_keyword = Keyword()
        new_keyword.project_id = project_id
        new_keyword.keyword = keyword_text
        new_keyword.category = category
        
        db.session.add(new_keyword)
        db.session.commit()
        
        return jsonify({
            'message': '키워드가 추가되었습니다.',
            'keyword': new_keyword.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@keyword_bp.route('/<int:keyword_id>', methods=['PUT'])
def update_keyword(keyword_id):
    """키워드 수정 API"""
    try:
        keyword = Keyword.query.get(keyword_id)
        
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

@keyword_bp.route('/<int:keyword_id>', methods=['DELETE'])
def delete_keyword(keyword_id):
    """키워드 삭제 API"""
    try:
        keyword = Keyword.query.get(keyword_id)
        
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
def upload_keywords(project_id):
    """CSV 파일로 키워드 업로드 API"""
    try:
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
        
        # 기존 키워드 삭제 (선택사항)
        if request.form.get('replace') == 'true':
            Keyword.query.filter_by(project_id=project_id).delete()
        
        # 새 키워드 추가
        added_count = 0
        for row in csv_reader:
            keyword_text = row.get('keyword', '').strip()
            category = row.get('category', '기타').strip()
            
            if keyword_text:
                new_keyword = Keyword()
                new_keyword.project_id = project_id
                new_keyword.keyword = keyword_text
                new_keyword.category = category
                
                db.session.add(new_keyword)
                added_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'{added_count}개의 키워드가 업로드되었습니다.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@keyword_bp.route('/projects/<int:project_id>/keywords/download', methods=['GET'])
def download_keywords(project_id):
    """키워드 CSV 다운로드 API"""
    try:
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        
        if not keywords:
            return jsonify({'error': '다운로드할 키워드가 없습니다.'}), 404
        
        # CSV 생성
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['keyword', 'category'])
        
        for keyword in keywords:
            writer.writerow([keyword.keyword, keyword.category])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=keywords_{project_id}.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500
