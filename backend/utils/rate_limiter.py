"""
요청 속도 제한 유틸리티
크롤링 시 서버에 과부하를 주지 않도록 요청 속도를 제한하는 모듈
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque
from threading import Lock

logger = logging.getLogger(__name__)


class RateLimiter:
    """요청 속도 제한기"""
    
    def __init__(self, requests_per_second: float = 1.0, burst_size: int = 5):
        """
        속도 제한기 초기화
        
        Args:
            requests_per_second: 초당 허용 요청 수
            burst_size: 버스트 허용 크기
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.min_interval = 1.0 / requests_per_second
        
        # 요청 기록
        self.request_times = deque()
        self.last_request_time = 0
        
        # 스레드 안전을 위한 락
        self.lock = Lock()
        
        # 통계
        self.stats = {
            'total_requests': 0,
            'delayed_requests': 0,
            'total_delay_time': 0.0
        }
    
    def wait(self) -> float:
        """
        요청 전 대기 시간 적용
        
        Returns:
            실제 대기 시간 (초)
        """
        with self.lock:
            current_time = time.time()
            
            # 마지막 요청 이후 경과 시간
            time_since_last = current_time - self.last_request_time
            
            # 최소 간격보다 짧으면 대기
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
                self.stats['delayed_requests'] += 1
                self.stats['total_delay_time'] += sleep_time
                actual_wait = sleep_time
            else:
                actual_wait = 0.0
            
            # 요청 시간 기록
            self.request_times.append(current_time)
            self.last_request_time = current_time
            
            # 오래된 기록 제거 (1초 이전)
            while self.request_times and current_time - self.request_times[0] > 1.0:
                self.request_times.popleft()
            
            # 버스트 크기 초과 시 추가 대기
            if len(self.request_times) > self.burst_size:
                oldest_request = self.request_times[0]
                required_wait = 1.0 - (current_time - oldest_request)
                if required_wait > 0:
                    time.sleep(required_wait)
                    actual_wait += required_wait
                    self.stats['delayed_requests'] += 1
                    self.stats['total_delay_time'] += required_wait
            
            self.stats['total_requests'] += 1
            return actual_wait
    
    def get_stats(self) -> Dict[str, float]:
        """
        속도 제한 통계 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        with self.lock:
            avg_delay = 0.0
            if self.stats['delayed_requests'] > 0:
                avg_delay = self.stats['total_delay_time'] / self.stats['delayed_requests']
            
            return {
                'total_requests': self.stats['total_requests'],
                'delayed_requests': self.stats['delayed_requests'],
                'total_delay_time': self.stats['total_delay_time'],
                'average_delay': avg_delay,
                'requests_per_second': self.requests_per_second,
                'burst_size': self.burst_size
            }
    
    def reset_stats(self):
        """통계 초기화"""
        with self.lock:
            self.stats = {
                'total_requests': 0,
                'delayed_requests': 0,
                'total_delay_time': 0.0
            }


class DomainRateLimiter:
    """도메인별 속도 제한기"""
    
    def __init__(self, default_requests_per_second: float = 1.0):
        """
        도메인별 속도 제한기 초기화
        
        Args:
            default_requests_per_second: 기본 초당 요청 수
        """
        self.default_requests_per_second = default_requests_per_second
        self.limiters: Dict[str, RateLimiter] = {}
        self.lock = Lock()
        
        # 도메인별 설정
        self.domain_settings = {
            'google.com': 0.5,      # Google은 더 느리게
            'github.com': 0.3,      # GitHub은 매우 느리게
            'stackoverflow.com': 0.5,  # Stack Overflow도 느리게
            'docs.github.com': 0.2,    # GitHub Docs는 매우 느리게
        }
    
    def get_limiter(self, domain: str) -> RateLimiter:
        """
        도메인에 대한 속도 제한기 반환
        
        Args:
            domain: 도메인명
            
        Returns:
            해당 도메인의 속도 제한기
        """
        with self.lock:
            if domain not in self.limiters:
                requests_per_second = self.domain_settings.get(domain, self.default_requests_per_second)
                self.limiters[domain] = RateLimiter(requests_per_second)
                logger.info(f"도메인별 속도 제한기 생성: {domain} ({requests_per_second} req/s)")
            
            return self.limiters[domain]
    
    def wait(self, domain: str) -> float:
        """
        도메인별 요청 대기
        
        Args:
            domain: 도메인명
            
        Returns:
            실제 대기 시간 (초)
        """
        limiter = self.get_limiter(domain)
        return limiter.wait()
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """
        모든 도메인의 통계 반환
        
        Returns:
            도메인별 통계 딕셔너리
        """
        with self.lock:
            stats = {}
            for domain, limiter in self.limiters.items():
                stats[domain] = limiter.get_stats()
            return stats
    
    def reset_all_stats(self):
        """모든 도메인의 통계 초기화"""
        with self.lock:
            for limiter in self.limiters.values():
                limiter.reset_stats()


class AdaptiveRateLimiter:
    """적응형 속도 제한기 (응답 시간에 따라 속도 조절)"""
    
    def __init__(self, initial_requests_per_second: float = 1.0, 
                 min_requests_per_second: float = 0.1,
                 max_requests_per_second: float = 5.0):
        """
        적응형 속도 제한기 초기화
        
        Args:
            initial_requests_per_second: 초기 초당 요청 수
            min_requests_per_second: 최소 초당 요청 수
            max_requests_per_second: 최대 초당 요청 수
        """
        self.requests_per_second = initial_requests_per_second
        self.min_requests_per_second = min_requests_per_second
        self.max_requests_per_second = max_requests_per_second
        
        self.limiter = RateLimiter(self.requests_per_second)
        
        # 응답 시간 기록
        self.response_times = deque(maxlen=10)
        self.error_count = 0
        self.success_count = 0
        
        # 조정 임계값
        self.slow_threshold = 2.0  # 2초 이상이면 느림
        self.fast_threshold = 0.5  # 0.5초 이하면 빠름
        self.error_threshold = 3   # 3번 연속 오류 시 속도 감소
    
    def wait(self) -> float:
        """
        요청 전 대기
        
        Returns:
            실제 대기 시간 (초)
        """
        return self.limiter.wait()
    
    def record_response(self, response_time: float, success: bool = True):
        """
        응답 시간 기록
        
        Args:
            response_time: 응답 시간 (초)
            success: 성공 여부
        """
        self.response_times.append(response_time)
        
        if success:
            self.success_count += 1
            self.error_count = 0
        else:
            self.error_count += 1
        
        # 속도 조정
        self._adjust_rate()
    
    def _adjust_rate(self):
        """응답 시간에 따른 속도 조정"""
        if len(self.response_times) < 5:
            return
        
        avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # 오류가 많으면 속도 감소
        if self.error_count >= self.error_threshold:
            self._decrease_rate()
            self.error_count = 0
            logger.info(f"오류 증가로 속도 감소: {self.requests_per_second:.2f} req/s")
            return
        
        # 응답 시간에 따른 조정
        if avg_response_time > self.slow_threshold:
            # 응답이 느리면 속도 감소
            self._decrease_rate()
            logger.info(f"응답 시간 느림 ({avg_response_time:.2f}s) - 속도 감소: {self.requests_per_second:.2f} req/s")
        elif avg_response_time < self.fast_threshold and self.success_count >= 5:
            # 응답이 빠르고 성공이 많으면 속도 증가
            self._increase_rate()
            logger.info(f"응답 시간 빠름 ({avg_response_time:.2f}s) - 속도 증가: {self.requests_per_second:.2f} req/s")
            self.success_count = 0
    
    def _increase_rate(self):
        """속도 증가"""
        new_rate = min(self.requests_per_second * 1.2, self.max_requests_per_second)
        if new_rate != self.requests_per_second:
            self.requests_per_second = new_rate
            self.limiter = RateLimiter(self.requests_per_second)
    
    def _decrease_rate(self):
        """속도 감소"""
        new_rate = max(self.requests_per_second * 0.8, self.min_requests_per_second)
        if new_rate != self.requests_per_second:
            self.requests_per_second = new_rate
            self.limiter = RateLimiter(self.requests_per_second)
    
    def get_stats(self) -> Dict[str, float]:
        """
        통계 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        stats = self.limiter.get_stats()
        stats['adaptive_rate'] = self.requests_per_second
        stats['error_count'] = self.error_count
        stats['success_count'] = self.success_count
        
        if self.response_times:
            stats['avg_response_time'] = sum(self.response_times) / len(self.response_times)
            stats['min_response_time'] = min(self.response_times)
            stats['max_response_time'] = max(self.response_times)
        
        return stats
