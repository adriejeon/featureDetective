import React, { useState, useEffect, useRef } from "react";
import { featureDetectionAPI } from "../services/api";
import {
  websocketService,
  JobProgress,
  JobCompleted,
  JobFailed,
} from "../services/websocket";
import "./FeatureDetection.css";

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
  const [competitorUrls, setCompetitorUrls] = useState<string>("");
  const [ourProductUrls, setOurProductUrls] = useState<string>("");
  const [projectName, setProjectName] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<FeatureDetectionResult | null>(null);
  const [error, setError] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"input" | "results">("input");

  // Job 관련 상태
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobProgress, setJobProgress] = useState<JobProgress | null>(null);
  const [jobStatus, setJobStatus] = useState<string>("");
  const [isWebSocketConnected, setIsWebSocketConnected] =
    useState<boolean>(false);

  // 웹소켓 연결 관리
  const socketRef = useRef<boolean>(false);

  // 웹소켓 연결 및 이벤트 리스너 설정
  useEffect(() => {
    const connectWebSocket = async () => {
      console.log("웹소켓 연결 시도 중...");
      try {
        await websocketService.connect();
        console.log("웹소켓 연결 성공!");
        setIsWebSocketConnected(true);
        socketRef.current = true;

        // 웹소켓 이벤트 리스너 설정
        websocketService.onConnected((data) => {
          console.log("웹소켓 연결됨:", data);
          setIsWebSocketConnected(true);
        });

        websocketService.onJoinedJob((data) => {
          console.log("Job 구독 성공:", data);
        });

        websocketService.onJobProgress((data: JobProgress) => {
          console.log("Job 진행률 업데이트:", data);
          setJobProgress(data);
          setJobStatus(data.status);
          console.log(
            "진행률 상태 업데이트됨:",
            data.progress + "%",
            data.current_step
          );
        });

        websocketService.onJobFailed((data: JobFailed) => {
          console.log("Job 실패:", data);
          setJobProgress({
            progress: 0,
            current_step: "실패",
            status: "failed",
          });
          setJobStatus("failed");
          setError(data.error || "기능 탐지 중 오류가 발생했습니다.");
          setIsLoading(false);
          setCurrentJobId(null);
        });

        websocketService.onJobCompleted((data: JobCompleted) => {
          console.log("Job 완료:", data);
          console.log("받은 데이터 구조:", JSON.stringify(data.data, null, 2));
          setJobProgress({
            progress: 100,
            current_step: "완료",
            status: "completed",
          });
          setJobStatus("completed");
          setResult(data.data);
          setIsLoading(false);
          setCurrentJobId(null);

          // 3초 후 결과 탭으로 이동
          setTimeout(() => {
            setActiveTab("results");
          }, 3000);
        });
      } catch (error) {
        console.error("웹소켓 연결 실패:", error);
        setIsWebSocketConnected(false);
      }
    };

    connectWebSocket();

    // 컴포넌트 언마운트 시 웹소켓 연결 해제
    return () => {
      if (currentJobId) {
        websocketService.leaveJob(currentJobId);
      }
      websocketService.disconnect();
      socketRef.current = false;
    };
  }, [currentJobId]);

  const handleDetectFeatures = async () => {
    console.log("기능 탐지 시작...");
    console.log("웹소켓 연결 상태:", isWebSocketConnected);

    if (!competitorUrls.trim() && !ourProductUrls.trim()) {
      setError("최소 하나의 URL이 필요합니다.");
      return;
    }

    setIsLoading(true);
    setError("");
    setJobProgress(null);
    setJobStatus("");

    try {
      const competitorUrlList = competitorUrls
        .split("\n")
        .filter((url) => url.trim());
      const ourProductUrlList = ourProductUrls
        .split("\n")
        .filter((url) => url.trim());

      console.log("API 호출 시작...");
      const response = await featureDetectionAPI.detectFeatures(
        competitorUrlList,
        ourProductUrlList,
        projectName || "기능 탐지 프로젝트"
      );
      console.log("API 응답:", response);

      if (response.data.success) {
        const jobId = response.data.data.job_id;
        setCurrentJobId(jobId);
        setJobStatus(response.data.data.status);
        setJobProgress({
          progress: response.data.data.progress,
          current_step: response.data.data.current_step,
          status: response.data.data.status,
        });

        // 웹소켓으로 Job 진행률 구독
        console.log("=== Job 구독 시도 ===");
        console.log("웹소켓 연결 상태:", isWebSocketConnected);
        console.log("Job ID:", jobId);

        if (isWebSocketConnected) {
          console.log("웹소켓 연결됨, Job 구독 시작:", jobId);
          websocketService.joinJob(jobId);
          console.log("Job 구독 요청 완료");
        } else {
          console.log("웹소켓 연결되지 않음, Job 구독 실패");
          console.log("웹소켓 재연결 시도...");
          // 웹소켓 재연결 시도
          websocketService
            .connect()
            .then(() => {
              console.log("웹소켓 재연결 성공, Job 구독 시도");
              websocketService.joinJob(jobId);
            })
            .catch((error) => {
              console.error("웹소켓 재연결 실패:", error);
            });
        }

        // 결과 탭으로 이동하지 않고 입력 탭에 머물러서 진행률 확인
        // setActiveTab("results");
      } else {
        setError(response.data.error || "기능 탐지 중 오류가 발생했습니다.");
        setIsLoading(false);
      }
    } catch (error: any) {
      console.error("기능 탐지 오류:", error);
      console.error("에러 상세:", error.response?.data);
      setError(
        error.response?.data?.error || "기능 탐지 중 오류가 발생했습니다."
      );
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

    const { comparison_analysis } = result.analysis_results || {};
    if (!comparison_analysis) {
      console.log("비교 분석 데이터가 없습니다:", result.analysis_results);
      return <div>비교 분석 데이터를 불러올 수 없습니다.</div>;
    }

    const { comparison_summary, competitive_analysis } = comparison_analysis;

    return (
      <div className="comparison-results">
        <h3>기능 비교 분석</h3>

        <div className="summary-cards">
          <div className="summary-card">
            <h4>경쟁사 기능</h4>
            <div className="number">
              {comparison_summary.total_features_product1}
            </div>
          </div>
          <div className="summary-card">
            <h4>우리 제품 기능</h4>
            <div className="number">
              {comparison_summary.total_features_product2}
            </div>
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
                {competitive_analysis.product2_advantages.map(
                  (advantage, index) => (
                    <li key={index}>{advantage}</li>
                  )
                )}
              </ul>
            </div>
            <div className="advantage-section">
              <h5>경쟁사의 장점</h5>
              <ul>
                {competitive_analysis.product1_advantages.map(
                  (advantage, index) => (
                    <li key={index}>{advantage}</li>
                  )
                )}
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

        {/* 웹소켓 연결 상태 표시 */}
        <div className="connection-status">
          <span
            className={`status-indicator ${
              isWebSocketConnected ? "connected" : "disconnected"
            }`}
          >
            {isWebSocketConnected ? "●" : "○"}
          </span>
          <span className="status-text">
            {isWebSocketConnected ? "실시간 연결됨" : "연결 중..."}
          </span>
          {currentJobId && (
            <span className="job-status-text">Job ID: {currentJobId}</span>
          )}
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === "input" ? "active" : ""}`}
          onClick={() => setActiveTab("input")}
        >
          분석 설정
        </button>
        <button
          className={`tab ${activeTab === "results" ? "active" : ""}`}
          onClick={() => setActiveTab("results")}
          disabled={!result}
        >
          분석 결과
        </button>
      </div>

      {activeTab === "input" && (
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
            <label htmlFor="ourProductUrls">
              우리 제품 URL (한 줄에 하나씩)
            </label>
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
            {isLoading ? "분석 중..." : "기능 탐지 시작"}
          </button>

          {/* Job 진행률 표시 */}
          {jobProgress && (
            <div className="job-progress">
              <div className="progress-header">
                <h3>🔍 AI 기능 분석 진행률</h3>
                <span className={`job-status ${jobStatus}`}>
                  {jobStatus === "pending" && "⏳ 대기 중"}
                  {jobStatus === "running" && "🔄 실행 중"}
                  {jobStatus === "completed" && "✅ 완료"}
                  {jobStatus === "failed" && "❌ 실패"}
                </span>
              </div>

              <div className="progress-bar-container">
                <div
                  className="progress-bar"
                  style={{ width: `${jobProgress.progress}%` }}
                ></div>
                <span className="progress-text">{jobProgress.progress}%</span>
              </div>

              <div className="current-step">
                <p>📋 {jobProgress.current_step}</p>
              </div>

              {/* 진행률 단계별 설명 */}
              <div className="progress-stages">
                <div
                  className={`stage ${
                    jobProgress.progress >= 10 ? "completed" : ""
                  }`}
                >
                  <span className="stage-icon">🌐</span>
                  <span className="stage-text">웹사이트 크롤링</span>
                </div>
                <div
                  className={`stage ${
                    jobProgress.progress >= 40 ? "completed" : ""
                  }`}
                >
                  <span className="stage-icon">🤖</span>
                  <span className="stage-text">Vertex AI 분석</span>
                </div>
                <div
                  className={`stage ${
                    jobProgress.progress >= 80 ? "completed" : ""
                  }`}
                >
                  <span className="stage-icon">🔍</span>
                  <span className="stage-text">기능 비교 분석</span>
                </div>
                <div
                  className={`stage ${
                    jobProgress.progress >= 90 ? "completed" : ""
                  }`}
                >
                  <span className="stage-icon">📊</span>
                  <span className="stage-text">결과 정리</span>
                </div>
              </div>
            </div>
          )}

          {isLoading && !jobProgress && (
            <div className="loading-info">
              <p>웹사이트 크롤링 및 AI 분석을 진행 중입니다...</p>
              <p>시간이 오래 걸릴 수 있습니다.</p>
              <p>
                웹소켓 연결 상태:{" "}
                {isWebSocketConnected ? "연결됨" : "연결 안됨"}
              </p>
            </div>
          )}
        </div>
      )}

      {activeTab === "results" && result && (
        <div className="results-section">
          {(() => {
            console.log("=== 결과 데이터 상세 분석 ===");
            console.log("전체 결과:", result);
            console.log("분석 결과:", result.analysis_results);

            const competitorFeatures =
              result.analysis_results?.competitor_features
                ?.extracted_features || [];
            const ourProductFeatures =
              result.analysis_results?.our_product_features
                ?.extracted_features || [];
            const mergedFeatures =
              (result.analysis_results as any)?.merged_features || [];
            const productFeatureMapping =
              (result.analysis_results as any)?.product_feature_mapping || {};

            console.log("경쟁사 기능 수:", competitorFeatures.length);
            console.log("우리 제품 기능 수:", ourProductFeatures.length);
            console.log("병합된 기능 수:", mergedFeatures.length);
            console.log("제품별 기능 매핑:", productFeatureMapping);

            // 첫 번째 기능들의 상세 정보 출력
            if (competitorFeatures.length > 0) {
              console.log("첫 번째 경쟁사 기능:", competitorFeatures[0]);
            }
            if (ourProductFeatures.length > 0) {
              console.log("첫 번째 우리 제품 기능:", ourProductFeatures[0]);
            }
            if (mergedFeatures.length > 0) {
              console.log("첫 번째 병합된 기능:", mergedFeatures[0]);
            }

            return null;
          })()}

          <div className="project-info">
            <h3>프로젝트 정보</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">프로젝트명:</span>
                <span className="value">{result.project_info.name}</span>
              </div>
              <div className="info-item">
                <span className="label">처리 시간:</span>
                <span className="value">
                  {result.project_info.processing_time_seconds.toFixed(2)}초
                </span>
              </div>
              <div className="info-item">
                <span className="label">크롤링 페이지:</span>
                <span className="value">
                  {result.project_info.total_pages_crawled}개
                </span>
              </div>
              <div className="info-item">
                <span className="label">분석 품질:</span>
                <span className="value">{result.summary.analysis_quality}</span>
              </div>
            </div>
          </div>

          <div className="analysis-results">
            {renderFeatureList(
              result.analysis_results?.competitor_features
                ?.extracted_features || [],
              "경쟁사 기능 분석"
            )}

            {renderFeatureList(
              result.analysis_results?.our_product_features
                ?.extracted_features || [],
              "우리 제품 기능 분석"
            )}

            {renderComparisonResults()}
          </div>
        </div>
      )}
    </div>
  );
};

export default FeatureDetection;
