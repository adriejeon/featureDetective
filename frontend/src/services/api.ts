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

// 고급 크롤링 API
export const advancedCrawlingAPI = {
  // 고급 사이트 크롤링
  crawlSiteAdvanced: (projectId: number, baseUrl: string, config?: any) =>
    apiClient.post('/advanced-crawling/crawl-site', {
      project_id: projectId,
      base_url: baseUrl,
      config
    }),

              // 헬프 센터 크롤링
            crawlHelpCenter: (projectId: number, baseUrl: string) => {
              const requestData = {
                project_id: projectId,
                base_url: baseUrl
              };
              console.log("헬프 센터 크롤링 API 요청 데이터:", requestData);
              console.log("요청 데이터 JSON:", JSON.stringify(requestData));
              console.log("projectId 타입:", typeof projectId);
              console.log("baseUrl 타입:", typeof baseUrl);
              return apiClient.post('/advanced-crawling/crawl-help-center', requestData);
            },

  // 문서 사이트 크롤링
  crawlDocumentation: (projectId: number, baseUrl: string) =>
    apiClient.post('/advanced-crawling/crawl-documentation', {
      project_id: projectId,
      base_url: baseUrl
    }),

  // 사용자 정의 설정으로 크롤링
  crawlWithCustomSettings: (
    projectId: number, 
    baseUrl: string, 
    settings: {
      include_patterns?: string[];
      exclude_patterns?: string[];
      css_exclude_selectors?: string[];
      max_pages?: number;
      max_depth?: number;
    }
  ) =>
    apiClient.post('/advanced-crawling/crawl-custom', {
      project_id: projectId,
      base_url: baseUrl,
      ...settings
    }),

  // 크롤링 상태 조회
  getAdvancedCrawlingStatus: (projectId: number) =>
    apiClient.get(`/advanced-crawling/status/${projectId}`),

  // 크롤링 결과 내보내기
  exportCrawlResults: (projectId: number, format: 'json' | 'csv', filepath?: string) =>
    apiClient.post(`/advanced-crawling/export/${projectId}`, {
      format,
      filepath
    }),

  // 크롤링 설정 템플릿 조회
  getConfigTemplates: () =>
    apiClient.get('/advanced-crawling/config/templates'),
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
