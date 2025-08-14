#!/usr/bin/env python3
"""
API 응답 구조 테스트
"""

import requests
import json

def test_feature_detection_api():
    """기능 탐지 API 테스트"""
    url = "http://localhost:5003/api/feature-detection/detect-features"
    
    data = {
        "competitor_urls": ["https://slack.com/help/articles/115004071768-What-is-Slack-"],
        "our_product_urls": ["https://support.discord.com/hc/en-us/articles/360045138571-Getting-Started"],
        "project_name": "API 테스트 프로젝트"
    }
    
    try:
        print("API 호출 중...")
        response = requests.post(url, json=data, timeout=30)
        
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 헤더: {response.headers}")
        
        if response.status_code == 200:
            result = response.json()
            print("API 응답 성공!")
            print("응답 구조:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 데이터 구조 확인
            if 'data' in result and 'job_id' in result['data']:
                job_id = result['data']['job_id']
                print(f"Job ID: {job_id}")
                
                # Job 상태 확인
                job_url = f"http://localhost:5003/api/jobs/{job_id}"
                job_response = requests.get(job_url)
                if job_response.status_code == 200:
                    job_data = job_response.json()
                    print("Job 상태:")
                    print(json.dumps(job_data, indent=2, ensure_ascii=False))
                else:
                    print(f"Job 상태 조회 실패: {job_response.status_code}")
            else:
                print("Job ID를 찾을 수 없습니다.")
        else:
            print(f"API 호출 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")
            
    except Exception as e:
        print(f"API 테스트 중 오류: {e}")

if __name__ == "__main__":
    test_feature_detection_api()
