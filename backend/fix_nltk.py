#!/usr/bin/env python3
"""
NLTK 데이터 로딩 문제 해결 스크립트
"""

import ssl
import nltk
import os

def fix_nltk_data():
    """NLTK 데이터 로딩 문제 해결"""
    print("NLTK 데이터 로딩 문제 해결 중...")
    
    # SSL 검증 비활성화
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # NLTK 데이터 다운로드
    try:
        print("wordnet 다운로드 중...")
        nltk.download('wordnet', quiet=True)
        print("omw-1.4 다운로드 중...")
        nltk.download('omw-1.4', quiet=True)
        print("✅ NLTK 데이터 다운로드 완료!")
        
        # 데이터 경로 확인
        data_path = nltk.data.path
        print(f"NLTK 데이터 경로: {data_path}")
        
        # wordnet 로딩 테스트
        from nltk.corpus import wordnet
        synsets = wordnet.synsets('test')
        print(f"WordNet 테스트 성공: {len(synsets)} synsets found")
        
        return True
        
    except Exception as e:
        print(f"❌ NLTK 데이터 다운로드 실패: {e}")
        return False

if __name__ == "__main__":
    success = fix_nltk_data()
    if success:
        print("\n🎉 NLTK 데이터 문제 해결 완료!")
    else:
        print("\n💥 NLTK 데이터 문제 해결 실패!")
