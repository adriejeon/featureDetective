from flask import Blueprint, request, jsonify
from models.project import Project
from models.keyword import Keyword
from models.feature_analysis import FeatureAnalysis
from services.report_service import ReportService
import csv
import io

report_bp = Blueprint('report', __name__)

@report_bp.route('/projects/<int:project_id>/report/pdf', methods=['GET'])
def generate_pdf_report(project_id):
    """PDF 리포트 생성 API"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 리포트 서비스로 PDF 생성
        report_service = ReportService()
        pdf_data = report_service.generate_pdf_report(project_id)
        
        from flask import Response
        return Response(
            pdf_data,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=report_{project_id}.pdf'}
        )
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@report_bp.route('/projects/<int:project_id>/report/csv', methods=['GET'])
def generate_csv_report(project_id):
    """CSV 리포트 생성 API"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 리포트 서비스로 CSV 생성
        report_service = ReportService()
        csv_data = report_service.generate_csv_report(project_id)
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=report_{project_id}.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@report_bp.route('/projects/<int:project_id>/report/summary', methods=['GET'])
def get_report_summary(project_id):
    """리포트 요약 정보 조회 API"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        # 키워드 및 분석 결과 조회
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        analyses = FeatureAnalysis.query.filter_by(project_id=project_id).all()
        
        # 요약 통계 계산
        total_keywords = len(keywords)
        total_analyses = len(analyses)
        
        support_stats = {
            'O': len([a for a in analyses if a.support_status == 'O']),
            'X': len([a for a in analyses if a.support_status == 'X']),
            '△': len([a for a in analyses if a.support_status == '△'])
        }
        
        return jsonify({
            'project': project.to_dict(),
            'summary': {
                'total_keywords': total_keywords,
                'total_analyses': total_analyses,
                'support_stats': support_stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@report_bp.route('/projects/<int:project_id>/report/analysis', methods=['GET'])
def get_detailed_analysis(project_id):
    """상세 분석 결과 조회 API"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '프로젝트를 찾을 수 없습니다.'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 페이지네이션으로 분석 결과 조회
        analyses = FeatureAnalysis.query.filter_by(
            project_id=project_id
        ).order_by(FeatureAnalysis.analyzed_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 키워드 정보 포함
        analysis_data = []
        for analysis in analyses.items:
            keyword = Keyword.query.get(analysis.keyword_id)
            analysis_data.append({
                **analysis.to_dict(),
                'keyword': keyword.keyword if keyword else '',
                'category': keyword.category if keyword else ''
            })
        
        return jsonify({
            'analyses': analysis_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': analyses.total,
                'pages': analyses.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500
