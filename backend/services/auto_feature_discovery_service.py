import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import json
from typing import Dict, List, Tuple, Optional, Set
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import numpy as np
from collections import defaultdict
import itertools

class AutoFeatureDiscoveryService:
    """자동 기능 발견 서비스"""
    
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
        
        # 기능 관련 키워드 사전
        self.feature_keywords = {
            # 채팅/메시징
            '채팅': ['chat', 'message', 'messaging', 'conversation', 'talk', 'communication'],
            '메시지': ['message', 'text', 'send', 'receive', 'reply', 'forward'],
            '그룹': ['group', 'team', 'channel', 'room', 'workspace', 'organization'],
            
            # 파일/미디어
            '파일': ['file', 'document', 'attachment', 'upload', 'download', 'share'],
            '이미지': ['image', 'photo', 'picture', 'gif', 'emoji', 'sticker'],
            '비디오': ['video', 'call', 'meeting', 'conference', 'stream', 'record'],
            '음성': ['voice', 'audio', 'call', 'phone', 'speak', 'talk'],
            
            # 앱/플랫폼
            '앱': ['app', 'application', 'mobile', 'desktop', 'web', 'browser'],
            '모바일': ['mobile', 'phone', 'smartphone', 'ios', 'android', 'app'],
            '데스크톱': ['desktop', 'computer', 'pc', 'mac', 'windows', 'application'],
            
            # 봇/자동화
            '봇': ['bot', 'chatbot', 'automation', 'workflow', 'integration', 'api'],
            '자동': ['auto', 'automatic', 'automation', 'workflow', 'trigger', 'scheduled'],
            
            # 보안/관리
            '보안': ['security', 'privacy', 'encryption', 'authentication', 'permission', 'access'],
            '관리': ['admin', 'management', 'settings', 'configuration', 'control', 'dashboard'],
            
            # 알림/통지
            '알림': ['notification', 'alert', 'reminder', 'push', 'email', 'sms'],
            '설정': ['setting', 'configuration', 'preference', 'option', 'customize', 'personalize'],
            
            # 검색/필터
            '검색': ['search', 'find', 'filter', 'query', 'lookup', 'discover'],
            '필터': ['filter', 'sort', 'organize', 'categorize', 'tag', 'label'],
            
            # 백업/동기화
            '백업': ['backup', 'sync', 'synchronization', 'export', 'import', 'restore'],
            '동기화': ['sync', 'synchronization', 'cloud', 'storage', 'backup', 'restore'],
            
            # 분석/리포팅
            '분석': ['analytics', 'report', 'statistics', 'insight', 'data', 'metrics'],
            '통계': ['statistics', 'analytics', 'report', 'data', 'metrics', 'insight']
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
    
    def discover_and_compare_features(self, competitor_url: str, our_product_url: str) -> Dict:
        """자동 기능 발견 및 비교"""
        try:
            # 두 URL에서 텍스트 크롤링
            competitor_text = self._crawl_and_extract_text(competitor_url)
            our_product_text = self._crawl_and_extract_text(our_product_url)
            
            # 기능 섹션 추출
            competitor_features = self._extract_feature_sections(competitor_text)
            our_product_features = self._extract_feature_sections(our_product_text)
            
            # 기능 클러스터링 및 매칭
            matched_features = self._match_features(competitor_features, our_product_features)
            
            # 분석 결과 생성
            analysis_results = self._analyze_matched_features(matched_features, competitor_text, our_product_text)
            
            return {
                'success': True,
                'data': {
                    'competitor_url': competitor_url,
                    'our_product_url': our_product_url,
                    'discovered_features': len(matched_features),
                    'results': analysis_results,
                    'competitor_features_count': len(competitor_features),
                    'our_product_features_count': len(our_product_features)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def _crawl_and_extract_text(self, url: str) -> str:
        """URL에서 텍스트 추출"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 불필요한 태그 제거
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
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
            
        except Exception as e:
            print(f"크롤링 오류 ({url}): {e}")
            return ""
    
    def _extract_feature_sections(self, text: str) -> List[Dict]:
        """텍스트에서 기능 섹션 추출"""
        features = []
        
        # 문장 단위로 분리
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # 너무 짧은 문장 제외
                continue
            
            # 기능 관련 키워드가 포함된 문장 찾기
            feature_score = self._calculate_feature_score(sentence)
            
            if feature_score > 0.3:  # 임계값
                features.append({
                    'text': sentence,
                    'score': feature_score,
                    'keywords': self._extract_keywords(sentence)
                })
        
        # 점수순으로 정렬
        features.sort(key=lambda x: x['score'], reverse=True)
        
        return features[:50]  # 상위 50개만 반환
    
    def _calculate_feature_score(self, text: str) -> float:
        """텍스트의 기능 관련 점수 계산"""
        text_lower = text.lower()
        score = 0.0
        
        # 기능 키워드 매칭
        for category, keywords in self.feature_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    score += 0.1
        
        # 긍정 표현 가중치
        for indicator in self.positive_indicators:
            if indicator in text_lower:
                score += 0.2
        
        # 부정 표현 감점
        for indicator in self.negative_indicators:
            if indicator in text_lower:
                score -= 0.1
        
        return max(0, score)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        text_lower = text.lower()
        keywords = []
        
        for category, category_keywords in self.feature_keywords.items():
            for keyword in category_keywords:
                if keyword in text_lower:
                    keywords.append(keyword)
        
        return list(set(keywords))
    
    def _match_features(self, competitor_features: List[Dict], our_product_features: List[Dict]) -> List[Dict]:
        """기능 매칭"""
        matched_features = []
        
        # TF-IDF 벡터화
        all_texts = [f['text'] for f in competitor_features + our_product_features]
        
        if len(all_texts) < 2:
            return matched_features
        
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # 코사인 유사도 계산
            similarities = cosine_similarity(tfidf_matrix)
            
            # 매칭 임계값
            threshold = 0.3
            
            # 경쟁사와 우리 제품 간 유사도 계산
            comp_count = len(competitor_features)
            our_count = len(our_product_features)
            
            for i in range(comp_count):
                for j in range(our_count):
                    similarity = similarities[i][comp_count + j]
                    
                    if similarity > threshold:
                        matched_features.append({
                            'competitor_feature': competitor_features[i],
                            'our_product_feature': our_product_features[j],
                            'similarity': similarity,
                            'feature_name': self._generate_feature_name(
                                competitor_features[i]['text'], 
                                our_product_features[j]['text']
                            )
                        })
            
            # 유사도순으로 정렬
            matched_features.sort(key=lambda x: x['similarity'], reverse=True)
            
            # 중복 제거 (유사한 매칭 중 최고 점수만 유지)
            unique_features = []
            used_competitor = set()
            used_our_product = set()
            
            for match in matched_features:
                comp_idx = competitor_features.index(match['competitor_feature'])
                our_idx = our_product_features.index(match['our_product_feature'])
                
                if comp_idx not in used_competitor and our_idx not in used_our_product:
                    unique_features.append(match)
                    used_competitor.add(comp_idx)
                    used_our_product.add(our_idx)
            
            return unique_features[:20]  # 상위 20개만 반환
            
        except Exception as e:
            print(f"매칭 오류: {e}")
            return matched_features
    
    def _generate_feature_name(self, comp_text: str, our_text: str) -> str:
        """기능 이름 생성"""
        # 공통 키워드 찾기
        comp_keywords = set(self._extract_keywords(comp_text))
        our_keywords = set(self._extract_keywords(our_text))
        common_keywords = comp_keywords.intersection(our_keywords)
        
        if common_keywords:
            # 가장 긴 공통 키워드 반환
            return max(common_keywords, key=len)
        
        # 공통 키워드가 없으면 첫 번째 키워드 반환
        all_keywords = list(comp_keywords) + list(our_keywords)
        if all_keywords:
            return all_keywords[0]
        
        return "기능"
    
    def _analyze_matched_features(self, matched_features: List[Dict], competitor_text: str, our_product_text: str) -> List[Dict]:
        """매칭된 기능 분석"""
        results = []
        
        for match in matched_features:
            comp_feature = match['competitor_feature']
            our_feature = match['our_product_feature']
            
            # 각 기능의 지원 여부 분석
            comp_support = self._analyze_support_status(comp_feature['text'], competitor_text)
            our_support = self._analyze_support_status(our_feature['text'], our_product_text)
            
            results.append({
                'feature_name': match['feature_name'],
                'similarity': round(match['similarity'], 3),
                'competitor': {
                    'status': comp_support['status'],
                    'confidence': comp_support['confidence'],
                    'text': comp_feature['text'][:100] + '...' if len(comp_feature['text']) > 100 else comp_feature['text']
                },
                'our_product': {
                    'status': our_support['status'],
                    'confidence': our_support['confidence'],
                    'text': our_feature['text'][:100] + '...' if len(our_feature['text']) > 100 else our_feature['text']
                }
            })
        
        return results
    
    def _analyze_support_status(self, feature_text: str, full_text: str) -> Dict:
        """기능 지원 상태 분석"""
        feature_lower = feature_text.lower()
        full_lower = full_text.lower()
        
        # 긍정 표현 확인
        positive_count = sum(1 for indicator in self.positive_indicators if indicator in feature_lower)
        negative_count = sum(1 for indicator in self.negative_indicators if indicator in feature_lower)
        
        if positive_count > negative_count:
            return {
                'status': 'O',
                'confidence': min(0.8 + positive_count * 0.1, 0.95)
            }
        elif negative_count > positive_count:
            return {
                'status': 'X',
                'confidence': min(0.8 + negative_count * 0.1, 0.95)
            }
        else:
            return {
                'status': '△',
                'confidence': 0.6
            }
