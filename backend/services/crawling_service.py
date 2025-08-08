import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
from models.crawling_result import CrawlingResult, db
from models.keyword import Keyword
from models.feature_analysis import FeatureAnalysis
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class CrawlingService:
    """크롤링 서비스 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # NLTK 데이터 다운로드 (처음 실행 시)
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def crawl_url(self, url, project_id):
        """URL 크롤링 및 분석"""
        crawling_result = None
        try:
            # 크롤링 결과 생성
            crawling_result = CrawlingResult()
            crawling_result.project_id = project_id
            crawling_result.url = url
            crawling_result.status = 'processing'
            db.session.add(crawling_result)
            db.session.commit()
            
            # 웹페이지 크롤링
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 텍스트 추출
            text_content = self._extract_text(soup)
            
            # 크롤링 결과 업데이트
            crawling_result.content = text_content
            crawling_result.status = 'completed'
            db.session.commit()
            
            # 키워드 분석
            self._analyze_keywords(project_id, url, text_content)
            
            return crawling_result
            
        except Exception as e:
            # 에러 처리
            if crawling_result:
                crawling_result.status = 'failed'
                crawling_result.error_message = str(e)
                db.session.commit()
            
            raise e
    
    def _extract_text(self, soup):
        """HTML에서 텍스트 추출"""
        # 불필요한 태그 제거
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        # 텍스트 추출
        text = soup.get_text()
        
        # 텍스트 정리
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # 특수문자 정리
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _analyze_keywords(self, project_id, url, text_content):
        """키워드 분석 및 기능 지원 여부 판별"""
        # 프로젝트의 키워드 조회
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        
        for keyword in keywords:
            # 키워드 매칭 및 분석
            support_status, confidence_score, matched_text = self._analyze_keyword_support(
                keyword.keyword, text_content
            )
            
            # 분석 결과 저장
            analysis = FeatureAnalysis()
            analysis.project_id = project_id
            analysis.keyword_id = keyword.id
            analysis.url = url
            analysis.support_status = support_status
            analysis.confidence_score = confidence_score
            analysis.matched_text = matched_text
            
            db.session.add(analysis)
        
        db.session.commit()
    
    def _analyze_keyword_support(self, keyword, text_content):
        """키워드 지원 여부 분석"""
        # 텍스트 전처리
        text_lower = text_content.lower()
        keyword_lower = keyword.lower()
        
        # 직접 매칭 (정확한 키워드)
        if keyword_lower in text_lower:
            return 'O', 0.9, keyword
        
        # 부분 매칭 (키워드의 일부가 포함된 경우)
        keyword_words = keyword_lower.split()
        if len(keyword_words) > 1:
            matched_words = [word for word in keyword_words if word in text_lower]
            if len(matched_words) >= len(keyword_words) * 0.7:
                return '△', 0.7, ', '.join(matched_words)
        
        # 유사 키워드 매칭
        similar_keywords = self._find_similar_keywords(keyword_lower, text_lower)
        if similar_keywords:
            return '△', 0.6, ', '.join(similar_keywords[:3])
        
        # 부정 키워드 확인
        negative_indicators = ['지원하지 않음', '불가능', '제한', '없음', '미지원', 'not supported', 'unavailable']
        for indicator in negative_indicators:
            if indicator in text_lower:
                return 'X', 0.8, indicator
        
        # 기본값: 미지원
        return 'X', 0.5, ''
    
    def _find_similar_keywords(self, keyword, text):
        """유사 키워드 찾기"""
        # 키워드를 단어로 분리
        keyword_words = set(word_tokenize(keyword))
        
        # 텍스트에서 유사한 단어 찾기
        text_words = set(word_tokenize(text))
        
        # 공통 단어 찾기
        common_words = keyword_words.intersection(text_words)
        
        if len(common_words) >= len(keyword_words) * 0.5:
            return list(common_words)
        
        return []
    
    def get_crawling_status(self, project_id):
        """크롤링 상태 조회"""
        results = CrawlingResult.query.filter_by(project_id=project_id).all()
        
        status_summary = {
            'total': len(results),
            'completed': len([r for r in results if r.status == 'completed']),
            'processing': len([r for r in results if r.status == 'processing']),
            'failed': len([r for r in results if r.status == 'failed']),
            'pending': len([r for r in results if r.status == 'pending'])
        }
        
        return status_summary, results
