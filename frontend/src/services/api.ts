import axios, { AxiosInstance, AxiosResponse } from "axios";

// API 기본 설정
const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://127.0.0.1:5003/api";

// Axios 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 응답 인터셉터 (에러 처리)
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    console.error("API 오류:", error);
    return Promise.reject(error);
  }
);

// 타입 정의
export interface Project {
  id: number;
  name: string;
  description: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  keyword_count: number;
  crawling_count: number;
}

export interface Keyword {
  id: number;
  project_id: number;
  keyword: string;
  category: string;
  created_at: string;
}

export interface CrawlingResult {
  id: number;
  project_id: number;
  url: string;
  content: string;
  status: string;
  error_message: string;
  crawled_at: string;
}

export interface FeatureAnalysis {
  id: number;
  project_id: number;
  keyword_id: number;
  url: string;
  support_status: "O" | "X" | "△";
  confidence_score: number;
  matched_text: string;
  analyzed_at: string;
}

// 프로젝트 API
export const projectAPI = {
  getProjects: () => apiClient.get("/projects/"),

  createProject: (name: string, description: string) =>
    apiClient.post("/projects/", { name, description }),

  getProject: (id: number) => apiClient.get(`/projects/${id}/`),

  updateProject: (id: number, data: { name?: string; description?: string }) =>
    apiClient.put(`/projects/${id}/`, data),

  deleteProject: (id: number) => apiClient.delete(`/projects/${id}/`),
};

// 키워드 API
export const keywordAPI = {
  getKeywords: (projectId: number) =>
    apiClient.get(`/keywords/projects/${projectId}/keywords`),

  createKeyword: (projectId: number, keyword: string, category: string) =>
    apiClient.post(`/keywords/projects/${projectId}/keywords`, {
      keyword,
      category,
    }),

  updateKeyword: (
    keywordId: number,
    data: { keyword?: string; category?: string }
  ) => apiClient.put(`/keywords/${keywordId}`, data),

  deleteKeyword: (keywordId: number) =>
    apiClient.delete(`/keywords/${keywordId}`),

  uploadKeywords: (projectId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post(
      `/keywords/projects/${projectId}/keywords/upload`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
  },

  downloadKeywords: (projectId: number) =>
    apiClient.get(`/keywords/projects/${projectId}/keywords/download`, {
      responseType: "blob",
    }),
};

// 크롤링 API
export const crawlingAPI = {
  startCrawling: (projectId: number, urls: string[]) =>
    apiClient.post(`/crawling/projects/${projectId}/crawl`, { urls }),

  getCrawlingStatus: (projectId: number) =>
    apiClient.get(`/crawling/projects/${projectId}/crawl/status`),

  getCrawlingResults: (projectId: number, page = 1, perPage = 20) =>
    apiClient.get(`/crawling/projects/${projectId}/results`, {
      params: { page, per_page: perPage },
    }),

  getCrawlingResult: (resultId: number) =>
    apiClient.get(`/crawling/results/${resultId}`),

  deleteCrawlingResult: (resultId: number) =>
    apiClient.delete(`/crawling/results/${resultId}`),
};

// 자동 기능 발견 API
export const autoDiscoveryAPI = {
  // 자동 기능 발견
  discoverFeatures: (competitorUrl: string, ourProductUrl: string) =>
    apiClient.post("/auto-discovery/discover", {
      competitor_url: competitorUrl,
      our_product_url: ourProductUrl,
    }),

  // 크롤링 결과 조회
  getCrawlingResults: (competitorUrl: string, ourProductUrl: string) =>
    apiClient.post("/auto-discovery/crawling-results", {
      competitor_url: competitorUrl,
      our_product_url: ourProductUrl,
    }),
};

// 통합 기능 탐지 API
export const featureDetectionAPI = {
  // URL 목록에서 기능 탐지 및 분석 (비동기 Job)
  detectFeatures: (
    competitorUrls: string[],
    ourProductUrls: string[],
    projectName: string
  ) =>
    apiClient.post("/feature-detection/detect-features", {
      competitor_urls: competitorUrls,
      our_product_urls: ourProductUrls,
      project_name: projectName,
    }),

  // 단일 URL에서 기능 분석
  analyzeSingleUrl: (url: string, companyName: string) =>
    apiClient.post("/feature-detection/analyze-single-url", {
      url: url,
      company_name: companyName,
    }),

  // 특정 URL에서 키워드 지원 여부 분석
  analyzeKeywordSupport: (url: string, keyword: string) =>
    apiClient.post("/feature-detection/analyze-keyword-support", {
      url: url,
      keyword: keyword,
    }),

  // 서비스 상태 확인
  checkHealth: () => apiClient.get("/feature-detection/health"),

  // Vertex AI 연결 테스트
  testVertexAI: (testText: string) =>
    apiClient.post("/feature-detection/test-vertex-ai", {
      test_text: testText,
    }),
};

// Job 관리 API
export const jobAPI = {
  // Job 상태 조회
  getJobStatus: (jobId: string) => apiClient.get(`/jobs/${jobId}`),

  // 프로젝트의 모든 Job 조회
  getProjectJobs: (projectId: number) =>
    apiClient.get(`/projects/${projectId}/jobs`),

  // Job 취소
  cancelJob: (jobId: string) => apiClient.post(`/jobs/${jobId}/cancel`),

  // Job 재시도
  retryJob: (jobId: string) => apiClient.post(`/jobs/${jobId}/retry`),
};

// 리포트 API
export const reportAPI = {
  generatePDFReport: (projectId: number) =>
    apiClient.get(`/reports/projects/${projectId}/report/pdf`, {
      responseType: "blob",
    }),

  generateCSVReport: (projectId: number) =>
    apiClient.get(`/reports/projects/${projectId}/report/csv`, {
      responseType: "blob",
    }),

  getReportSummary: (projectId: number) =>
    apiClient.get(`/reports/projects/${projectId}/report/summary`),

  getDetailedAnalysis: (projectId: number, page = 1, perPage = 20) =>
    apiClient.get(`/reports/projects/${projectId}/report/analysis`, {
      params: { page, per_page: perPage },
    }),
};

// 헬스체크 API
export const healthAPI = {
  checkHealth: () => apiClient.get("/health"),
};

export default apiClient;
