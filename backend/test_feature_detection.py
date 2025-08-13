#!/usr/bin/env python3
"""
통합 기능 탐지 시스템 테스트 스크립트
"""

import asyncio
import json
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.feature_detection_service import FeatureDetectionService

async def test_vertex_ai_connection():
    """Vertex AI 연결 테스트"""
    print("=== Vertex AI 연결 테스트 ===")
    
    try:
        service = FeatureDetectionService()
        
        # 간단한 텍스트로 기능 추출 테스트
        test_text = """
        우리 제품은 다음과 같은 기능을 제공합니다:
        - 실시간 채팅 기능
        - 파일 업로드 및 공유
        - 화상 회의 기능
        - 사용자 권한 관리
        - 데이터 백업 및 복원
        """
        
        result = service.vertex_ai.extract_features_from_text("테스트 제품", test_text)
        
        print("✅ Vertex AI 연결 성공!")
        print(f"추출된 기능 수: {len(result.get('extracted_features', []))}")
        
        if result.get('extracted_features'):
            print("추출된 기능 예시:")
            for feature in result['extracted_features'][:3]:
                print(f"  - {feature.get('name', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vertex AI 연결 실패: {e}")
        return False

async def test_single_url_analysis():
    """단일 URL 분석 테스트"""
    print("\n=== 단일 URL 분석 테스트 ===")
    
    try:
        service = FeatureDetectionService()
        
        # 테스트용 URL (실제 존재하는 웹사이트)
        test_url = "https://www.notion.so"
        company_name = "Notion"
        
        print(f"분석 중: {test_url}")
        result = await service.analyze_single_url(test_url, company_name)
        
        if result.get('success'):
            print("✅ 단일 URL 분석 성공!")
            print(f"크롤링된 페이지 수: {result.get('pages_crawled', 0)}")
            
            features = result.get('features', {})
            feature_count = len(features.get('extracted_features', []))
            print(f"추출된 기능 수: {feature_count}")
            
            if feature_count > 0:
                print("추출된 기능 예시:")
                for feature in features['extracted_features'][:3]:
                    print(f"  - {feature.get('name', 'N/A')} ({feature.get('category', 'N/A')})")
            
            return True
        else:
            print(f"❌ 단일 URL 분석 실패: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 단일 URL 분석 오류: {e}")
        return False

async def test_keyword_analysis():
    """키워드 지원 분석 테스트"""
    print("\n=== 키워드 지원 분석 테스트 ===")
    
    try:
        service = FeatureDetectionService()
        
        test_url = "https://www.slack.com"
        test_keyword = "화상회의"
        
        print(f"키워드 분석 중: {test_url} - '{test_keyword}'")
        result = await service.analyze_keyword_support(test_url, test_keyword)
        
        if result.get('success'):
            print("✅ 키워드 분석 성공!")
            
            analysis = result.get('analysis', {})
            support_status = analysis.get('support_status', 'N/A')
            confidence = analysis.get('confidence_score', 0)
            
            print(f"지원 상태: {support_status}")
            print(f"신뢰도: {confidence}")
            print(f"분석 근거: {analysis.get('analysis_reason', 'N/A')}")
            
            return True
        else:
            print(f"❌ 키워드 분석 실패: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 키워드 분석 오류: {e}")
        return False

async def test_feature_comparison():
    """기능 비교 분석 테스트"""
    print("\n=== 기능 비교 분석 테스트 ===")
    
    try:
        service = FeatureDetectionService()
        
        # 테스트용 URL들
        competitor_urls = ["https://www.slack.com"]
        our_product_urls = ["https://www.notion.so"]
        
        print("기능 비교 분석 시작...")
        print(f"경쟁사: {competitor_urls}")
        print(f"우리 제품: {our_product_urls}")
        
        result = await service.detect_features_from_urls(
            competitor_urls, 
            our_product_urls, 
            "테스트 프로젝트"
        )
        
        if not result.get('error'):
            print("✅ 기능 비교 분석 성공!")
            
            project_info = result.get('project_info', {})
            crawling_results = result.get('crawling_results', {})
            analysis_results = result.get('analysis_results', {})
            
            print(f"처리 시간: {project_info.get('processing_time_seconds', 0):.2f}초")
            print(f"총 크롤링 페이지: {crawling_results.get('competitor_pages', 0) + crawling_results.get('our_product_pages', 0)}")
            
            # 기능 수 비교
            competitor_features = analysis_results.get('competitor_features', {})
            our_features = analysis_results.get('our_product_features', {})
            
            comp_feature_count = len(competitor_features.get('extracted_features', []))
            our_feature_count = len(our_features.get('extracted_features', []))
            
            print(f"경쟁사 기능 수: {comp_feature_count}")
            print(f"우리 제품 기능 수: {our_feature_count}")
            
            # 비교 분석 결과
            comparison = analysis_results.get('comparison_analysis', {})
            if comparison:
                print("비교 분석 결과:")
                summary = comparison.get('comparison_summary', {})
                print(f"  - 공통 기능: {summary.get('common_features', 0)}개")
                print(f"  - 경쟁사 고유 기능: {summary.get('unique_features_product1', 0)}개")
                print(f"  - 우리 제품 고유 기능: {summary.get('unique_features_product2', 0)}개")
            
            return True
        else:
            print(f"❌ 기능 비교 분석 실패: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 기능 비교 분석 오류: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 통합 기능 탐지 시스템 테스트 시작")
    print("=" * 50)
    
    # 테스트 결과 추적
    test_results = []
    
    # 1. Vertex AI 연결 테스트
    test_results.append(await test_vertex_ai_connection())
    
    # 2. 단일 URL 분석 테스트
    test_results.append(await test_single_url_analysis())
    
    # 3. 키워드 분석 테스트
    test_results.append(await test_keyword_analysis())
    
    # 4. 기능 비교 분석 테스트 (시간이 오래 걸릴 수 있음)
    print("\n⚠️  기능 비교 분석은 시간이 오래 걸릴 수 있습니다...")
    test_results.append(await test_feature_comparison())
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"통과한 테스트: {passed}/{total}")
    
    if passed == total:
        print("🎉 모든 테스트가 성공했습니다!")
        print("✅ 통합 기능 탐지 시스템이 정상적으로 작동합니다.")
    else:
        print("⚠️  일부 테스트가 실패했습니다.")
        print("🔧 설정을 확인하고 다시 시도해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 비동기 실행
    success = asyncio.run(main())
    
    if success:
        print("\n✅ 시스템 준비 완료! API 서버를 시작할 수 있습니다.")
        print("실행 명령어: python app.py")
    else:
        print("\n❌ 시스템 설정에 문제가 있습니다.")
        print("환경 변수와 Vertex AI 인증을 확인해주세요.")
        sys.exit(1)
