import React, { useState } from 'react';
import { featureDetectionAPI } from '../services/api';
import './FeatureDetection.css';

interface FeatureDetectionResult {
  project_info: {
    name: string;
    created_at: string;
    processing_time_seconds: number;
    total_pages_crawled: number;
  };
  crawling_results: {
    competitor_pages: number;
    our_product_pages: number;
    competitor_urls: string[];
    our_product_urls: string[];
  };
  analysis_results: {
    competitor_features: {
      extracted_features: Array<{
        name: string;
        category: string;
        description: string;
        confidence: number;
      }>;
      analysis_summary: {
        total_features: number;
        main_categories: string[];
        document_quality: string;
      };
    };
    our_product_features: {
      extracted_features: Array<{
        name: string;
        category: string;
        description: string;
        confidence: number;
      }>;
      analysis_summary: {
        total_features: number;
        main_categories: string[];
        document_quality: string;
      };
    };
    comparison_analysis: {
      comparison_summary: {
        total_features_product1: number;
        total_features_product2: number;
        common_features: number;
        unique_features_product1: number;
        unique_features_product2: number;
      };
      feature_comparison: Array<{
        feature_name: string;
        product1_support: boolean;
        product2_support: boolean;
        comparison_type: string;
        significance: string;
      }>;
      competitive_analysis: {
        product1_advantages: string[];
        product2_advantages: string[];
        market_positioning: string;
        recommendations: string[];
      };
    };
  };
  summary: {
    competitor_feature_count: number;
    our_product_feature_count: number;
    analysis_quality: string;
  };
}

const FeatureDetection: React.FC = () => {
  const [competitorUrls, setCompetitorUrls] = useState<string>('');
  const [ourProductUrls, setOurProductUrls] = useState<string>('');
  const [projectName, setProjectName] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<FeatureDetectionResult | null>(null);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'input' | 'results'>('input');

  const handleDetectFeatures = async () => {
    if (!competitorUrls.trim() && !ourProductUrls.trim()) {
      setError('최소 하나의 URL이 필요합니다.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const competitorUrlList = competitorUrls.split('\n').filter(url => url.trim());
      const ourProductUrlList = ourProductUrls.split('\n').filter(url => url.trim());

      const response = await featureDetectionAPI.detectFeatures(
        competitorUrlList,
        ourProductUrlList,
        projectName || '기능 탐지 프로젝트'
      );

      if (response.data.success) {
        setResult(response.data.data);
        setActiveTab('results');
      } else {
        setError(response.data.error || '분석 중 오류가 발생했습니다.');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || '서버 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderFeatureList = (features: any[], title: string) => (
    <div className="feature-list">
      <h3>{title}</h3>
      {features.length === 0 ? (
        <p className="no-features">추출된 기능이 없습니다.</p>
      ) : (
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <h4>{feature.name}</h4>
              <p className="category">{feature.category}</p>
              <p className="description">{feature.description}</p>
              <div className="confidence">
                신뢰도: {(feature.confidence * 100).toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderComparisonResults = () => {
    if (!result) return null;

    const { comparison_analysis } = result.analysis_results;
    const { comparison_summary, feature_comparison, competitive_analysis } = comparison_analysis;

    return (
      <div className="comparison-results">
        <h3>기능 비교 분석</h3>
        
        <div className="summary-cards">
          <div className="summary-card">
            <h4>경쟁사 기능</h4>
            <div className="number">{comparison_summary.total_features_product1}</div>
          </div>
          <div className="summary-card">
            <h4>우리 제품 기능</h4>
            <div className="number">{comparison_summary.total_features_product2}</div>
          </div>
          <div className="summary-card">
            <h4>공통 기능</h4>
            <div className="number">{comparison_summary.common_features}</div>
          </div>
        </div>

        <div className="competitive-analysis">
          <h4>경쟁 우위 분석</h4>
          <div className="advantages">
            <div className="advantage-section">
              <h5>우리 제품의 장점</h5>
              <ul>
                {competitive_analysis.product2_advantages.map((advantage, index) => (
                  <li key={index}>{advantage}</li>
                ))}
              </ul>
            </div>
            <div className="advantage-section">
              <h5>경쟁사의 장점</h5>
              <ul>
                {competitive_analysis.product1_advantages.map((advantage, index) => (
                  <li key={index}>{advantage}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="recommendations">
          <h4>개선 권장사항</h4>
          <ul>
            {competitive_analysis.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  return (
    <div className="feature-detection">
      <div className="header">
        <h1>통합 기능 탐지</h1>
        <p>Vertex AI를 활용한 지능형 기능 분석 및 비교</p>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'input' ? 'active' : ''}`}
          onClick={() => setActiveTab('input')}
        >
          분석 설정
        </button>
        <button
          className={`tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
          disabled={!result}
        >
          분석 결과
        </button>
      </div>

      {activeTab === 'input' && (
        <div className="input-section">
          <div className="form-group">
            <label htmlFor="projectName">프로젝트 이름</label>
            <input
              type="text"
              id="projectName"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="프로젝트 이름을 입력하세요"
            />
          </div>

          <div className="form-group">
            <label htmlFor="competitorUrls">경쟁사 URL (한 줄에 하나씩)</label>
            <textarea
              id="competitorUrls"
              value={competitorUrls}
              onChange={(e) => setCompetitorUrls(e.target.value)}
              placeholder="https://competitor1.com&#10;https://competitor2.com"
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="ourProductUrls">우리 제품 URL (한 줄에 하나씩)</label>
            <textarea
              id="ourProductUrls"
              value={ourProductUrls}
              onChange={(e) => setOurProductUrls(e.target.value)}
              placeholder="https://ourproduct.com"
              rows={4}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            className="detect-button"
            onClick={handleDetectFeatures}
            disabled={isLoading}
          >
            {isLoading ? '분석 중...' : '기능 탐지 시작'}
          </button>

          {isLoading && (
            <div className="loading-info">
              <p>웹사이트 크롤링 및 AI 분석을 진행 중입니다...</p>
              <p>시간이 오래 걸릴 수 있습니다.</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'results' && result && (
        <div className="results-section">
          <div className="project-info">
            <h3>프로젝트 정보</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">프로젝트명:</span>
                <span className="value">{result.project_info.name}</span>
              </div>
              <div className="info-item">
                <span className="label">처리 시간:</span>
                <span className="value">{result.project_info.processing_time_seconds.toFixed(2)}초</span>
              </div>
              <div className="info-item">
                <span className="label">크롤링 페이지:</span>
                <span className="value">{result.project_info.total_pages_crawled}개</span>
              </div>
              <div className="info-item">
                <span className="label">분석 품질:</span>
                <span className="value">{result.summary.analysis_quality}</span>
              </div>
            </div>
          </div>

          <div className="analysis-results">
            {renderFeatureList(
              result.analysis_results.competitor_features.extracted_features,
              '경쟁사 기능 분석'
            )}

            {renderFeatureList(
              result.analysis_results.our_product_features.extracted_features,
              '우리 제품 기능 분석'
            )}

            {renderComparisonResults()}
          </div>
        </div>
      )}
    </div>
  );
};

export default FeatureDetection;
