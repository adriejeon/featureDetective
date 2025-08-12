"""
Vertex AI 클라이언트 래퍼
Google Cloud 인증, API 호출, 에러 처리, 캐싱 기능 제공
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from functools import lru_cache
import hashlib

try:
    from google import genai
    from google.genai import types
    from google.auth import default
    from google.auth.exceptions import DefaultCredentialsError
except ImportError as e:
    logging.error(f"Google Cloud 라이브러리 import 실패: {e}")
    genai = None
    types = None

logger = logging.getLogger(__name__)


class VertexAIClient:
    """Vertex AI 클라이언트 래퍼"""
    
    def __init__(self, project_id: str = None, location: str = None, model: str = None):
        """
        Vertex AI 클라이언트 초기화
        
        Args:
            project_id: Google Cloud 프로젝트 ID
            location: Vertex AI 리전
            model: 사용할 모델명
        """
        self.project_id = project_id or os.getenv('VERTEX_AI_PROJECT_ID', 'groobee-ai')
        self.location = location or os.getenv('VERTEX_AI_LOCATION', 'global')
        self.model = model or os.getenv('VERTEX_AI_MODEL', 'gemini-2.5-flash-lite')
        self.client = None
        self._cache = {}
        self._rate_limit_delay = 1.0  # API 호출 간격 (초)
        self._last_call_time = 0
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Vertex AI 클라이언트 초기화"""
        try:
            # Google Cloud 인증 확인
            credentials, project = default()
            logger.info(f"Google Cloud 인증 성공: {project}")
            
            # Vertex AI 클라이언트 생성
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
            )
            logger.info(f"Vertex AI 클라이언트 초기화 완료: {self.project_id}")
            
        except DefaultCredentialsError:
            logger.warning("Google Cloud 기본 인증 정보를 찾을 수 없습니다.")
            logger.warning("다음 중 하나를 설정해주세요:")
            logger.warning("1. GOOGLE_APPLICATION_CREDENTIALS 환경변수 설정")
            logger.warning("2. gcloud auth application-default login 실행")
            logger.warning("인증 없이 기본 기능만 사용 가능합니다.")
            self.client = None
            
        except Exception as e:
            logger.warning(f"Vertex AI 클라이언트 초기화 실패: {e}")
            logger.warning("인증 없이 기본 기능만 사용 가능합니다.")
            self.client = None
    
    def _rate_limit(self):
        """API 호출 간격 조절"""
        current_time = time.time()
        time_since_last_call = current_time - self._last_call_time
        
        if time_since_last_call < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - time_since_last_call
            time.sleep(sleep_time)
        
        self._last_call_time = time.time()
    
    def _generate_cache_key(self, prompt: str, config: Dict = None) -> str:
        """캐시 키 생성"""
        cache_data = {
            'prompt': prompt,
            'config': config or {},
            'model': self.model
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """캐시된 응답 가져오기"""
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            # 캐시 만료 시간 확인 (1시간)
            if time.time() - cached_data['timestamp'] < 3600:
                logger.info("캐시된 응답 사용")
                return cached_data['response']
            else:
                del self._cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: Dict):
        """응답 캐시 저장"""
        self._cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.info("응답 캐시 저장")
    
    def generate_content(self, prompt: str, system_instruction: str = None, 
                        config: Dict = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Vertex AI로 콘텐츠 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항
            config: 생성 설정
            use_cache: 캐시 사용 여부
            
        Returns:
            생성된 콘텐츠와 메타데이터
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Vertex AI 클라이언트가 초기화되지 않았습니다.',
                'content': None
            }
        
        try:
            # 캐시 확인
            if use_cache:
                cache_key = self._generate_cache_key(prompt, config)
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    return cached_response
            
            # API 호출 간격 조절
            self._rate_limit()
            
            # 기본 설정
            default_config = {
                'temperature': 1,
                'top_p': 0.95,
                'max_output_tokens': 65535,
                'safety_settings': [
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
                ],
                'thinking_config': types.ThinkingConfig(thinking_budget=0),
            }
            
            # 사용자 설정으로 기본 설정 업데이트
            if config:
                default_config.update(config)
            
            # 시스템 지시사항 추가
            if system_instruction:
                default_config['system_instruction'] = [types.Part.from_text(text=system_instruction)]
            
            # 생성 설정 생성
            generate_config = types.GenerateContentConfig(**default_config)
            
            # 콘텐츠 생성
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]
            
            # API 호출
            logger.info(f"Vertex AI API 호출 시작: {self.model}")
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_config,
            )
            
            # 응답 처리
            response_text = response.text
            logger.info(f"Vertex AI 응답 수신: {len(response_text)}자")
            
            result = {
                'success': True,
                'content': response_text,
                'model': self.model,
                'timestamp': time.time()
            }
            
            # 캐시 저장
            if use_cache:
                self._cache_response(cache_key, result)
            
            return result
            
        except Exception as e:
            error_msg = f"Vertex AI API 호출 실패: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'content': None
            }
    
    def extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        응답 텍스트에서 JSON 추출
        
        Args:
            response_text: Vertex AI 응답 텍스트
            
        Returns:
            파싱된 JSON 객체
        """
        try:
            # JSON 블록이 있는 경우 추출
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text[json_start:].strip()
            else:
                # JSON 블록이 없는 경우 전체 텍스트를 JSON으로 파싱 시도
                json_text = response_text.strip()
            
            # JSON 파싱
            result = json.loads(json_text)
            logger.info("JSON 파싱 성공")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            logger.error(f"응답 텍스트: {response_text[:500]}...")
            return {
                'error': 'JSON 파싱 실패',
                'raw_response': response_text[:1000]
            }
    
    def is_available(self) -> bool:
        """Vertex AI 서비스 사용 가능 여부 확인"""
        return self.client is not None
    
    def get_status(self) -> Dict[str, Any]:
        """서비스 상태 정보 반환"""
        return {
            'available': self.is_available(),
            'project_id': self.project_id,
            'location': self.location,
            'model': self.model,
            'cache_size': len(self._cache)
        }
