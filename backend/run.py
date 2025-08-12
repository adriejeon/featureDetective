#!/usr/bin/env python3
"""
Feature Detective 백엔드 서버 실행 스크립트
"""

import os
from app import create_app, db

# 환경 변수 설정
os.environ.setdefault('FLASK_APP', 'app.py')
os.environ.setdefault('FLASK_ENV', 'development')

# Flask 앱 생성
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()
        print("데이터베이스 테이블이 생성되었습니다.")
    
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5002)
