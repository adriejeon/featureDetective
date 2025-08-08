import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import json
from typing import Dict, List, Tuple, Optional
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class FeatureAnalysisService:
    """고급 기능 분석 서비스"""
    
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
        
        # NLTK 데이터 초기화
        self._init_nltk()
        
        # 기능별 동의어 사전
        self.feature_synonyms = {
            # 채팅/메시징 관련
            '실시간 채팅': ['실시간 메시징', '라이브 채팅', '인스턴트 메시징', 'real-time chat', 'live chat', 'instant messaging'],
            '그룹 채팅': ['팀 채팅', '채널 채팅', '멀티 채팅', 'group chat', 'team chat', 'channel chat'],
            '개인 메시지': ['DM', '다이렉트 메시지', '1:1 채팅', 'private message', 'direct message'],
            
            # 파일/미디어 관련
            '파일 공유': ['파일 업로드', '파일 전송', '문서 공유', 'file sharing', 'file upload', 'document sharing'],
            '이미지 공유': ['사진 공유', '그림 공유', 'image sharing', 'photo sharing'],
            '화상 회의': ['비디오 통화', '화상 통화', '영상 회의', 'video call', 'video conference', 'web conference'],
            '음성 통화': ['보이스 콜', '전화 통화', 'voice call', 'audio call'],
            
            # 앱/플랫폼 관련
            '모바일 앱': ['스마트폰 앱', '휴대폰 앱', 'mobile app', 'smartphone app'],
            '데스크톱 앱': ['PC 앱', '컴퓨터 앱', 'desktop app', 'computer app'],
            '웹 앱': ['브라우저 앱', '웹 기반', 'web app', 'browser app'],
            
            # 봇/자동화 관련
            '봇 연동': ['챗봇', '자동 응답', '봇 설정', 'bot integration', 'chatbot', 'auto response'],
            '자동화': ['워크플로우', '자동 처리', 'automation', 'workflow'],
            
            # API/개발자 관련
            'API 제공': ['개발자 API', 'API 연동', 'developer api', 'api integration'],
            '웹훅': ['webhook', '이벤트 알림', 'event notification'],
            
            # 보안/관리 관련
            '보안 설정': ['보안 관리', '권한 설정', 'security settings', 'access control'],
            '관리자 도구': ['관리 패널', '어드민 도구', 'admin tools', 'management panel'],
            
            # 알림/통지 관련
            '푸시 알림': ['알림 설정', '메시지 알림', 'push notification', 'message alert'],
            '이메일 알림': ['메일 알림', 'email notification', 'email alert'],
            
            # 검색/필터 관련
            '메시지 검색': ['채팅 검색', '대화 검색', 'message search', 'chat search'],
            '필터링': ['메시지 필터', 'content filtering', 'message filter'],
            
            # 커스터마이징 관련
            '테마 설정': ['색상 테마', '디자인 커스터마이징', 'theme customization', 'color theme'],
            '언어 설정': ['다국어 지원', 'language settings', 'multilingual support'],
            
            # 백업/동기화 관련
            '메시지 백업': ['대화 백업', '채팅 백업', 'message backup', 'chat backup'],
            '동기화': ['데이터 동기화', 'sync', 'data synchronization'],
            
            # 분석/리포팅 관련
            '사용 통계': ['활용도 분석', '사용량 통계', 'usage statistics', 'analytics'],
            '리포팅': ['보고서 생성', '통계 리포트', 'reporting', 'statistics report']
        }
        
        # 부정 표현 사전
        self.negative_indicators = [
            '지원하지 않음', '불가능', '제한', '없음', '미지원', 'not supported', 'unavailable',
            '아직 개발 중', '준비 중', 'coming soon', 'under development',
            '프리미엄 기능', '유료 기능', 'premium feature', 'paid feature',
            '제한적 지원', 'limited support', 'partial support'
        ]
        
        # 긍정 표현 사전
        self.positive_indicators = [
            '지원', '가능', '제공', 'available', 'supported', 'enabled',
            '완전 지원', 'full support', 'comprehensive support',
            '무료 제공', 'free', 'included', '기본 기능', 'basic feature'
        ]
    
    def _init_nltk(self):
        """NLTK 데이터 초기화"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            nltk.download('omw-1.4')
    
    def analyze_features(self, competitor_url: str, our_product_url: str, features: List[str]) -> Dict:
        """기능 분석 메인 함수"""
        try:
            # 두 URL에서 텍스트 크롤링
            competitor_text = self._crawl_and_extract_text(competitor_url)
            our_product_text = self._crawl_and_extract_text(our_product_url)
            
            # 각 기능별 분석
            results = []
            for feature in features:
                feature = feature.strip()
                if not feature:
                    continue
                
                competitor_result = self._analyze_single_feature(feature, competitor_text)
                our_product_result = self._analyze_single_feature(feature, our_product_text)
                
                results.append({
                    'feature': feature,
                    'competitor': competitor_result,
                    'our_product': our_product_result
                })
            
            return {
                'success': True,
                'results': results,
                'competitor_url': competitor_url,
                'our_product_url': our_product_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def _crawl_and_extract_text(self, url: str) -> str:
        """URL에서 텍스트 추출"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 불필요한 태그 제거
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                tag.decompose()
            
            # 도움말/기능 관련 섹션 우선 추출
            feature_texts = []
            
            # 일반적인 도움말 페이지 구조에서 기능 관련 텍스트 찾기
            selectors = [
                'main', 'article', '.content', '.main-content', '.help-content',
                '.features', '.functionality', '.capabilities', '.documentation',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # 제목 태그들
                'p', 'li', 'div', 'span'  # 본문 태그들
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if len(text) > 20 and self._is_feature_related(text):
                        feature_texts.append(text)
            
            # 중복 제거 및 정리
            unique_texts = list(set(feature_texts))
            combined_text = ' '.join(unique_texts)
            
            # 텍스트 정리
            lines = (line.strip() for line in combined_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # 특수문자 정리
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            print(f"크롤링 오류 ({url}): {e}")
            return ""
    
    def _is_feature_related(self, text: str) -> bool:
        """텍스트가 기능 관련인지 확인"""
        text_lower = text.lower()
        
        # 기능 관련 키워드가 포함된 텍스트인지 확인
        feature_keywords = [
            'chat', 'message', 'file', 'video', 'call', 'bot', 'api',
            'mobile', 'desktop', 'security', 'notification', 'search',
            'backup', 'sync', 'analytics', 'report', 'setting', 'config',
            '채팅', '메시지', '파일', '비디오', '통화', '봇', '앱',
            '모바일', '보안', '알림', '검색', '백업', '동기화', '분석'
        ]
        
        return any(keyword in text_lower for keyword in feature_keywords)
    
    def _analyze_single_feature(self, feature: str, text: str) -> Dict:
        """단일 기능 분석"""
        text_lower = text.lower()
        feature_lower = feature.lower()
        
        # 1. 직접 매칭
        direct_match = self._check_direct_match(feature_lower, text_lower)
        if direct_match['found']:
            return direct_match
        
        # 2. 동의어 매칭
        synonym_match = self._check_synonym_match(feature_lower, text_lower)
        if synonym_match['found']:
            return synonym_match
        
        # 3. 문맥 분석
        context_match = self._check_context_match(feature_lower, text_lower)
        if context_match['found']:
            return context_match
        
        # 4. 유사도 분석
        similarity_match = self._check_similarity_match(feature_lower, text_lower)
        if similarity_match['found']:
            return similarity_match
        
        # 5. 부정 표현 확인
        negative_check = self._check_negative_indicators(text_lower)
        if negative_check['found']:
            return negative_check
        
        # 6. 기본 기능 확인 (채팅 서비스의 경우)
        if self._is_basic_feature(feature_lower):
            basic_check = self._check_basic_feature_support(feature_lower, text_lower)
            if basic_check['found']:
                return basic_check
        
        # 기본값: 미지원
        return {
            'status': 'X',
            'confidence': 0.3,
            'found': False,
            'matched_text': '',
            'reason': '기능을 찾을 수 없음'
        }
    
    def _is_basic_feature(self, feature: str) -> bool:
        """기본 기능인지 확인 (채팅 서비스에서 당연히 지원하는 기능들)"""
        basic_features = [
            'chat', 'message', 'messaging', '채팅', '메시지', '메시징',
            'conversation', 'talk', 'communication', '대화', '통신'
        ]
        return any(basic in feature for basic in basic_features)
    
    def _check_basic_feature_support(self, feature: str, text: str) -> Dict:
        """기본 기능 지원 여부 확인"""
        # 채팅 서비스에서 기본적으로 지원하는 기능들
        if 'chat' in feature or 'message' in feature or '채팅' in feature or '메시지' in feature:
            # 채팅 서비스라면 기본적으로 채팅 기능은 지원
            return {
                'status': 'O',
                'confidence': 0.9,
                'found': True,
                'matched_text': '기본 채팅 기능',
                'reason': '채팅 서비스의 기본 기능'
            }
        
        return {'found': False}
    
    def _check_direct_match(self, feature: str, text: str) -> Dict:
        """직접 매칭 확인"""
        if feature in text:
            return {
                'status': 'O',
                'confidence': 0.95,
                'found': True,
                'matched_text': feature,
                'reason': '정확한 키워드 매칭'
            }
        return {'found': False}
    
    def _check_synonym_match(self, feature: str, text: str) -> Dict:
        """동의어 매칭 확인"""
        # 기능별 동의어 찾기
        synonyms = []
        for key, value in self.feature_synonyms.items():
            if feature in key.lower() or key.lower() in feature:
                synonyms.extend(value)
        
        # 동의어 매칭 확인
        for synonym in synonyms:
            if synonym.lower() in text:
                return {
                    'status': 'O',
                    'confidence': 0.85,
                    'found': True,
                    'matched_text': synonym,
                    'reason': f'동의어 매칭: {synonym}'
                }
        
        return {'found': False}
    
    def _check_context_match(self, feature: str, text: str) -> Dict:
        """문맥 분석을 통한 매칭"""
        # 문장 단위로 분석
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # 기능 키워드가 문장에 포함되어 있는지 확인
            if any(word in sentence_lower for word in feature.split()):
                # 고급 기능인지 확인 (화상 회의, 봇 등)
                if self._is_advanced_feature(feature):
                    # 고급 기능은 명시적으로 언급되어야 함
                    if self._has_explicit_support(sentence_lower):
                        return {
                            'status': 'O',
                            'confidence': 0.85,
                            'found': True,
                            'matched_text': sentence[:100] + '...',
                            'reason': '문맥 분석: 명시적 지원 확인'
                        }
                    elif self._has_explicit_denial(sentence_lower):
                        return {
                            'status': 'X',
                            'confidence': 0.9,
                            'found': True,
                            'matched_text': sentence[:100] + '...',
                            'reason': '문맥 분석: 명시적 미지원 확인'
                        }
                    else:
                        return {
                            'status': '△',
                            'confidence': 0.6,
                            'found': True,
                            'matched_text': sentence[:100] + '...',
                            'reason': '문맥 분석: 불명확한 지원 상태'
                        }
                else:
                    # 기본 기능은 일반적인 분석
                    positive_count = sum(1 for indicator in self.positive_indicators if indicator in sentence_lower)
                    negative_count = sum(1 for indicator in self.negative_indicators if indicator in sentence_lower)
                    
                    if positive_count > negative_count:
                        return {
                            'status': 'O',
                            'confidence': 0.75,
                            'found': True,
                            'matched_text': sentence[:100] + '...',
                            'reason': '문맥 분석: 긍정적 표현 발견'
                        }
                    elif negative_count > positive_count:
                        return {
                            'status': 'X',
                            'confidence': 0.8,
                            'found': True,
                            'matched_text': sentence[:100] + '...',
                            'reason': '문맥 분석: 부정적 표현 발견'
                        }
                    else:
                        return {
                            'status': '△',
                            'confidence': 0.6,
                            'found': True,
                            'matched_text': sentence[:100] + '...',
                            'reason': '문맥 분석: 중립적 표현'
                        }
        
        return {'found': False}
    
    def _is_advanced_feature(self, feature: str) -> bool:
        """고급 기능인지 확인"""
        advanced_features = [
            'video', 'call', 'meeting', 'conference', '화상', '회의', '통화',
            'bot', 'chatbot', 'automation', '봇', '자동화',
            'api', 'integration', '연동',
            'analytics', 'report', '분석', '리포트'
        ]
        return any(advanced in feature for advanced in advanced_features)
    
    def _has_explicit_support(self, text: str) -> bool:
        """명시적 지원 표현 확인"""
        explicit_support = [
            'support', 'available', 'feature', 'include', 'provide', 'offer',
            '지원', '제공', '포함', '기능', '사용 가능', '이용 가능'
        ]
        return any(support in text for support in explicit_support)
    
    def _has_explicit_denial(self, text: str) -> bool:
        """명시적 부정 표현 확인"""
        explicit_denial = [
            'not support', 'not available', 'not include', 'not provide',
            '미지원', '지원하지 않음', '제공하지 않음', '포함하지 않음'
        ]
        return any(denial in text for denial in explicit_denial)
    
    def _check_similarity_match(self, feature: str, text: str) -> Dict:
        """유사도 분석을 통한 매칭"""
        try:
            # TF-IDF 벡터화
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=1000
            )
            
            # 텍스트를 청크로 나누기
            chunks = self._split_text_into_chunks(text, 500)
            
            if not chunks:
                return {'found': False}
            
            # 벡터화
            tfidf_matrix = vectorizer.fit_transform([feature] + chunks)
            
            # 코사인 유사도 계산
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            
            # 가장 유사한 청크 찾기
            max_similarity = np.max(similarities)
            best_chunk_idx = np.argmax(similarities)
            
            if max_similarity > 0.3:  # 임계값
                return {
                    'status': '△',
                    'confidence': min(max_similarity, 0.7),
                    'found': True,
                    'matched_text': chunks[best_chunk_idx][:100] + '...',
                    'reason': f'유사도 분석: {max_similarity:.2f}'
                }
        
        except Exception as e:
            print(f"유사도 분석 오류: {e}")
        
        return {'found': False}
    
    def _check_negative_indicators(self, text: str) -> Dict:
        """부정 표현 확인"""
        for indicator in self.negative_indicators:
            if indicator in text:
                return {
                    'status': 'X',
                    'confidence': 0.9,
                    'found': True,
                    'matched_text': indicator,
                    'reason': f'부정 표현 발견: {indicator}'
                }
        return {'found': False}
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """텍스트를 청크로 나누기"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:  # 최소 길이 확인
                chunks.append(chunk)
        
        return chunks
