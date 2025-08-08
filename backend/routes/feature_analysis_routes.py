from flask import Blueprint, request, jsonify
from services.feature_analysis_service import FeatureAnalysisService
import json

feature_analysis_bp = Blueprint('feature_analysis', __name__)
feature_service = FeatureAnalysisService()

@feature_analysis_bp.route('/analyze', methods=['POST'])
def analyze_features():
    """기능 분석 API"""
    try:
        data = request.get_json()
        
        # 필수 파라미터 확인
        required_fields = ['competitor_url', 'our_product_url', 'features']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        competitor_url = data['competitor_url']
        our_product_url = data['our_product_url']
        features = data['features']
        
        # features가 문자열인 경우 리스트로 변환
        if isinstance(features, str):
            features = [f.strip() for f in features.split(',') if f.strip()]
        
        # URL 유효성 검사
        if not competitor_url.startswith(('http://', 'https://')):
            return jsonify({'error': '경쟁사 URL이 유효하지 않습니다'}), 400
        
        if not our_product_url.startswith(('http://', 'https://')):
            return jsonify({'error': '우리 제품 URL이 유효하지 않습니다'}), 400
        
        # 기능 분석 실행
        result = feature_service.analyze_features(competitor_url, our_product_url, features)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '기능 분석이 완료되었습니다',
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'기능 분석 중 오류가 발생했습니다: {str(e)}'
        }), 500

@feature_analysis_bp.route('/synonyms', methods=['GET'])
def get_feature_synonyms():
    """기능별 동의어 목록 조회"""
    try:
        return jsonify({
            'success': True,
            'data': feature_service.feature_synonyms
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'동의어 목록 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@feature_analysis_bp.route('/test', methods=['POST'])
def test_analysis():
    """테스트용 분석 API (임시 결과 반환)"""
    try:
        data = request.get_json()
        
        competitor_url = data.get('competitor_url', '')
        our_product_url = data.get('our_product_url', '')
        features = data.get('features', [])
        
        # features가 문자열인 경우 리스트로 변환
        if isinstance(features, str):
            features = [f.strip() for f in features.split(',') if f.strip()]
        
        # 실제 분석 대신 테스트 결과 생성
        results = []
        for feature in features:
            # 실제 분석 로직을 시뮬레이션
            import random
            
            # 동의어 매칭 시뮬레이션
            has_synonym = random.random() > 0.5
            
            if has_synonym:
                competitor_status = 'O' if random.random() > 0.3 else '△'
                our_product_status = 'O' if random.random() > 0.4 else '△'
            else:
                competitor_status = 'X' if random.random() > 0.6 else '△'
                our_product_status = 'X' if random.random() > 0.5 else '△'
            
            results.append({
                'feature': feature,
                'competitor': {
                    'status': competitor_status,
                    'confidence': round(random.uniform(0.6, 0.95), 2),
                    'found': competitor_status != 'X',
                    'matched_text': f'테스트 매칭 결과: {feature}',
                    'reason': '테스트 분석'
                },
                'our_product': {
                    'status': our_product_status,
                    'confidence': round(random.uniform(0.6, 0.95), 2),
                    'found': our_product_status != 'X',
                    'matched_text': f'테스트 매칭 결과: {feature}',
                    'reason': '테스트 분석'
                }
            })
        
        return jsonify({
            'success': True,
            'message': '테스트 분석이 완료되었습니다',
            'data': {
                'results': results,
                'competitor_url': competitor_url,
                'our_product_url': our_product_url
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'테스트 분석 중 오류가 발생했습니다: {str(e)}'
        }), 500
