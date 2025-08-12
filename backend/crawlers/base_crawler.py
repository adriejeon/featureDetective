"""
기본 크롤러 추상 클래스
모든 크롤러의 기본이 되는 추상 클래스
"""

import abc
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseCrawler(abc.ABC):
    """크롤러 기본 클래스"""
    
    def __init__(self, rate_limit: float = 1.0, timeout: int = 30):
        """
        기본 크롤러 초기화
        
        Args:
            rate_limit: 요청 간 대기 시간 (초)
            timeout: 요청 타임아웃 (초)
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.last_request_time = 0
    
    def _rate_limit(self):
        """요청 간 대기 시간 적용"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        웹 페이지 가져오기
        
        Args:
            url: 가져올 URL
            
        Returns:
            BeautifulSoup 객체 또는 None
        """
        try:
            self._rate_limit()
            logger.info(f"페이지 요청: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 인코딩 문제 해결
            try:
                if response.encoding == 'ISO-8859-1':
                    response.encoding = response.apparent_encoding
                
                # UTF-8로 강제 변환 시도
                if not response.encoding or response.encoding.lower() not in ['utf-8', 'utf8']:
                    response.encoding = 'utf-8'
                
                soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)
            except:
                # 인코딩 실패 시 기본 파싱
                soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"페이지 로드 성공: {len(response.content)} bytes, 인코딩: {response.encoding}")
            
            return soup
            
        except requests.RequestException as e:
            logger.error(f"페이지 요청 실패 ({url}): {e}")
            return None
        except Exception as e:
            logger.error(f"페이지 파싱 실패 ({url}): {e}")
            return None
    
    def is_same_domain(self, base_url: str, target_url: str) -> bool:
        """
        같은 도메인인지 확인
        
        Args:
            base_url: 기준 URL
            target_url: 확인할 URL
            
        Returns:
            같은 도메인이면 True
        """
        try:
            base_domain = urlparse(base_url).netloc
            target_domain = urlparse(target_url).netloc
            
            # 같은 도메인이거나 하위 도메인인 경우
            return base_domain in target_domain or target_domain in base_domain
        except Exception:
            return False
    
    @abc.abstractmethod
    def crawl(self, url: str) -> List[Dict[str, Any]]:
        """
        크롤링 실행 (추상 메서드)
        
        Args:
            url: 크롤링할 URL
            
        Returns:
            크롤링된 데이터 리스트
        """
        pass
    
    @abc.abstractmethod
    def extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        콘텐츠 추출 (추상 메서드)
        
        Args:
            soup: BeautifulSoup 객체
            url: 페이지 URL
            
        Returns:
            추출된 텍스트
        """
        pass
    
    def clean_text(self, text: str) -> str:
        """
        텍스트 정리
        
        Args:
            text: 정리할 텍스트
            
        Returns:
            정리된 텍스트
        """
        import re
        
        # 불필요한 공백 제거
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # 특수문자 정리
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
