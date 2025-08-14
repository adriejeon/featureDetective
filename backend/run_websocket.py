#!/usr/bin/env python3
"""
웹소켓 서버 실행 스크립트
"""

import os
from app import create_app
from websocket_server import websocket_manager

# 환경 변수 설정
os.environ.setdefault('FLASK_APP', 'app.py')
os.environ.setdefault('FLASK_ENV', 'development')

# Flask 앱 생성
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # 데이터베이스 테이블 생성
        from extensions import db
        db.create_all()
        print("데이터베이스 테이블이 생성되었습니다.")
    
    # 웹소켓 서버 실행
    print("웹소켓 서버를 시작합니다... (포트: 5004)")
    websocket_manager.run(host='0.0.0.0', port=5004, debug=True)

