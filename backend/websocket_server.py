#!/usr/bin/env python3
"""
웹소켓 서버 - 실시간 진행률 업데이트
"""

import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

logger = logging.getLogger(__name__)

class WebSocketManager:
    """웹소켓 연결 관리자"""
    
    def __init__(self, app=None):
        self.app = app
        self.socketio = None
        self.connected_clients: Dict[str, Set[str]] = {}  # job_id -> client_sids
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 웹소켓 초기화"""
        self.app = app
        self.socketio = SocketIO(
            app, 
            cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
        
        self._register_handlers()
    
    def _register_handlers(self):
        """웹소켓 이벤트 핸들러 등록"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """클라이언트 연결"""
            logger.info(f"클라이언트 연결: {request.sid}")
            emit('connected', {'message': '연결되었습니다.'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """클라이언트 연결 해제"""
            logger.info(f"클라이언트 연결 해제: {request.sid}")
            self._remove_client_from_all_rooms(request.sid)
        
        @self.socketio.on('join_job')
        def handle_join_job(data):
            """Job 진행률 구독"""
            logger.info(f"join_job 이벤트 수신: {data}")
            job_id = data.get('job_id')
            logger.info(f"Job ID: {job_id}")
            
            if job_id:
                room_name = f"job_{job_id}"
                logger.info(f"룸 참가: {room_name}")
                join_room(room_name)
                
                if job_id not in self.connected_clients:
                    self.connected_clients[job_id] = set()
                self.connected_clients[job_id].add(request.sid)
                
                logger.info(f"클라이언트 {request.sid}가 Job {job_id} 구독")
                logger.info(f"현재 Job {job_id} 구독자: {self.connected_clients[job_id]}")
                
                emit('joined_job', {'job_id': job_id, 'message': f'Job {job_id} 진행률을 구독합니다.'})
            else:
                logger.error("Job ID가 없습니다")
        
        @self.socketio.on('leave_job')
        def handle_leave_job(data):
            """Job 진행률 구독 해제"""
            job_id = data.get('job_id')
            if job_id:
                leave_room(f"job_{job_id}")
                if job_id in self.connected_clients:
                    self.connected_clients[job_id].discard(request.sid)
                    if not self.connected_clients[job_id]:
                        del self.connected_clients[job_id]
                logger.info(f"클라이언트 {request.sid}가 Job {job_id} 구독 해제")
                emit('left_job', {'job_id': job_id, 'message': f'Job {job_id} 구독을 해제했습니다.'})
    
    def _remove_client_from_all_rooms(self, client_sid: str):
        """클라이언트를 모든 Job 룸에서 제거"""
        for job_id, clients in list(self.connected_clients.items()):
            if client_sid in clients:
                clients.discard(client_sid)
                if not clients:
                    del self.connected_clients[job_id]
    
    def emit_job_progress(self, job_id: str, progress_data: dict):
        """Job 진행률 업데이트 전송"""
        logger.info(f"=== 진행률 업데이트 시도 ===")
        logger.info(f"Job ID: {job_id}")
        logger.info(f"진행률 데이터: {progress_data}")
        logger.info(f"socketio 존재: {self.socketio is not None}")
        
        if self.socketio:
            room = f"job_{job_id}"
            logger.info(f"룸 이름: {room}")
            logger.info(f"Job {job_id} 구독자: {self.connected_clients.get(job_id, set())}")
            
            self.socketio.emit('job_progress', progress_data, room=room)
            logger.info(f"Job {job_id} 진행률 업데이트 전송 완료: {progress_data}")
        else:
            logger.error("socketio가 초기화되지 않았습니다")
    
    def emit_job_completed(self, job_id: str, result_data: dict):
        """Job 완료 알림 전송"""
        if self.socketio:
            room = f"job_{job_id}"
            self.socketio.emit('job_completed', result_data, room=room)
            logger.info(f"Job {job_id} 완료 알림 전송")
    
    def emit_job_failed(self, job_id: str, error_data: dict):
        """Job 실패 알림 전송"""
        if self.socketio:
            room = f"job_{job_id}"
            self.socketio.emit('job_failed', error_data, room=room)
            logger.info(f"Job {job_id} 실패 알림 전송")
    
    def run(self, host='0.0.0.0', port=5004, debug=True):
        """웹소켓 서버 실행"""
        if self.socketio:
            self.socketio.run(self.app, host=host, port=port, debug=debug)

# 전역 웹소켓 매니저 인스턴스
websocket_manager = WebSocketManager()
