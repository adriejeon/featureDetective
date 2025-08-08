from flask import Blueprint, request, jsonify
from services.auto_feature_discovery_service import AutoFeatureDiscoveryService
import json

auto_discovery_bp = Blueprint('auto_discovery', __name__)
auto_discovery_service = AutoFeatureDiscoveryService()

@auto_discovery_bp.route('/discover', methods=['POST'])
def discover_features():
    """자동 기능 발견 API"""
    try:
        data = request.get_json()
        
        # 필수 파라미터 확인
        required_fields = ['competitor_url', 'our_product_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        competitor_url = data['competitor_url']
        our_product_url = data['our_product_url']
        
        # URL 유효성 검사
        if not competitor_url.startswith(('http://', 'https://')):
            return jsonify({'error': '경쟁사 URL이 유효하지 않습니다'}), 400
        
        if not our_product_url.startswith(('http://', 'https://')):
            return jsonify({'error': '우리 제품 URL이 유효하지 않습니다'}), 400
        
        # 자동 기능 발견 실행
        result = auto_discovery_service.discover_and_compare_features(competitor_url, our_product_url)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '자동 기능 발견이 완료되었습니다',
                'data': result['data']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'자동 기능 발견 중 오류가 발생했습니다: {str(e)}'
        }), 500

@auto_discovery_bp.route('/test', methods=['POST'])
def test_discovery():
    """테스트용 자동 기능 발견 API"""
    try:
        data = request.get_json()
        
        competitor_url = data.get('competitor_url', '')
        our_product_url = data.get('our_product_url', '')
        
        # 실제 분석 대신 테스트 결과 생성
        import random
        
        # 테스트용 기능 목록
        test_features = [
            '채팅', '파일 공유', '화상 회의', '봇 연동', '모바일 앱', 
            'API 제공', '보안 설정', '알림', '검색', '백업'
        ]
        
        results = []
        for feature in test_features:
            # 유사도 시뮬레이션
            similarity = round(random.uniform(0.4, 0.9), 3)
            
            # 지원 상태 시뮬레이션
            comp_status = 'O' if random.random() > 0.3 else ('X' if random.random() > 0.5 else '△')
            our_status = 'O' if random.random() > 0.4 else ('X' if random.random() > 0.5 else '△')
            
            results.append({
                'feature_name': feature,
                'similarity': similarity,
                'competitor': {
                    'status': comp_status,
                    'confidence': round(random.uniform(0.7, 0.95), 2),
                    'text': f'경쟁사 {feature} 관련 설명 텍스트...'
                },
                'our_product': {
                    'status': our_status,
                    'confidence': round(random.uniform(0.7, 0.95), 2),
                    'text': f'우리 제품 {feature} 관련 설명 텍스트...'
                }
            })
        
        return jsonify({
            'success': True,
            'message': '테스트 자동 기능 발견이 완료되었습니다',
            'data': {
                'competitor_url': competitor_url,
                'our_product_url': our_product_url,
                'discovered_features': len(results),
                'results': results,
                'competitor_features_count': random.randint(15, 25),
                'our_product_features_count': random.randint(12, 22)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'테스트 자동 기능 발견 중 오류가 발생했습니다: {str(e)}'
        }), 500
