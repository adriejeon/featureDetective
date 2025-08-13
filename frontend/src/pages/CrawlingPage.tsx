import React from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
} from "@mui/material";
import {
  PlayArrow as PlayIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
} from "@mui/icons-material";
import { useParams, useNavigate } from "react-router-dom";
import { autoDiscoveryAPI } from "../services/api";

interface AnalysisResult {
  feature: string;
  competitor: "O" | "X" | "△";
  ourProduct: "O" | "X" | "△";
  competitorDescription?: string;
  ourProductDescription?: string;
  competitorLink?: string;
  ourProductLink?: string;
}

interface CrawlingFeature {
  title: string;
  content: string;
  url: string;
  source_page_title?: string;
  category?: string;
  granularity?: string;
}

interface CrawlingResults {
  competitor_features: CrawlingFeature[];
  our_product_features: CrawlingFeature[];
  competitor_features_count: number;
  our_product_features_count: number;
  crawling_status: string;
  timestamp: string;
}

interface VertexAIAnalysis {
  success: boolean;
  competitor_features: {
    extracted_features: Array<{
      name: string;
      category: string;
      description: string;
      confidence: number;
      source_pages: string[];
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
      source_pages: string[];
    }>;
    analysis_summary: {
      total_features: number;
      main_categories: string[];
      document_quality: string;
    };
  };
  comparison_analysis: {
    feature_comparison: Array<{
      feature_name: string;
      competitor_implementation: string;
      our_implementation: string;
      advantage: string;
      gap: string;
      priority: string;
    }>;
    competitive_analysis: {
      our_advantages: string[];
      competitor_advantages: string[];
      market_gaps: string[];
      recommendations: string[];
    };
    summary: {
      total_comparable_features: number;
      our_unique_features: number;
      competitor_unique_features: number;
      overall_assessment: string;
    };
  };
  analysis_method: string;
}

const CrawlingPage: React.FC = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [competitorName, setCompetitorName] = React.useState("");
  const [competitorUrl, setCompetitorUrl] = React.useState("");
  const [ourProductName, setOurProductName] = React.useState("");
  const [ourProductUrl, setOurProductUrl] = React.useState("");
  const [features, setFeatures] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const [results, setResults] = React.useState<AnalysisResult[]>([]);
  const [selectedResult, setSelectedResult] = React.useState<AnalysisResult | null>(null);
  const [detailModalOpen, setDetailModalOpen] = React.useState(false);
  const [crawlingResults, setCrawlingResults] = React.useState<CrawlingResults | null>(null);
  const [vertexAIAnalysis, setVertexAIAnalysis] = React.useState<VertexAIAnalysis | null>(null);
  const [activeTab, setActiveTab] = React.useState(0);
  const [loadingCrawlingResults, setLoadingCrawlingResults] = React.useState(false);


  const handleAnalyze = async () => {
    setError("");

    if (
      !competitorName.trim() ||
      !competitorUrl.trim() ||
      !ourProductName.trim() ||
      !ourProductUrl.trim()
    ) {
      setError("경쟁사와 우리 제품 정보를 모두 입력해주세요.");
      return;
    }

    setLoading(true);
    try {
      let apiResults: AnalysisResult[] = [];

      if (features.trim()) {
        // 수동 입력 모드
        const featureList = features
          .split(",")
          .map((f) => f.trim())
          .filter((f) => f);

        const response = await fetch(
          "http://127.0.0.1:5001/api/feature-analysis/analyze",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              competitor_url: competitorUrl.trim(),
              our_product_url: ourProductUrl.trim(),
              features: featureList,
            }),
          }
        );

        const data = await response.json();

        if (data.success) {
          // Vertex AI 분석 결과가 있는지 확인
          if (data.data.vertex_ai_analysis) {
            setVertexAIAnalysis(data.data.vertex_ai_analysis);
            console.log("Vertex AI 분석 결과:", data.data.vertex_ai_analysis);
          }
          
          // 기존 분석 결과도 처리
          if (data.data.results) {
            apiResults = data.data.results.map((result: any) => ({
              feature: result.feature,
              competitor: result.competitor.status,
              ourProduct: result.our_product.status,
              competitorDescription: result.competitor.text,
              ourProductDescription: result.our_product.text,
              competitorLink: competitorUrl,
              ourProductLink: ourProductUrl,
            }));
          }
        } else {
          setError(data.error || "분석 중 오류가 발생했습니다.");
          return;
        }
      } else {
        // 자동 발견 모드 (새로운 통합 기능 탐지 API 사용)
        console.log("통합 기능 탐지 모드 시작");
        const response = await fetch(
          "http://127.0.0.1:5001/api/feature-detection/detect-features",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              competitor_urls: [competitorUrl.trim()],
              our_product_urls: [ourProductUrl.trim()],
              project_name: "자동 기능 탐지 프로젝트"
            }),
          }
        );

        const data = await response.json();
        console.log("통합 기능 탐지 API 응답:", data); // 디버깅용

        if (data.success) {
          console.log("API 응답 데이터:", data); // 디버깅용
          
          // 통합 기능 탐지 결과 처리
          const analysisResults = data.data.analysis_results;
          const competitorFeatures = analysisResults.competitor_features.extracted_features || [];
          const ourProductFeatures = analysisResults.our_product_features.extracted_features || [];
          const comparisonAnalysis = analysisResults.comparison_analysis || {};
          
          // 기능 비교 결과 생성
          apiResults = [];
          
          // 경쟁사 기능들 처리
          for (const feature of competitorFeatures) {
            apiResults.push({
              feature: feature.name,
              competitor: 'O',
              ourProduct: 'X',
              competitorDescription: `${feature.description} (신뢰도: ${(feature.confidence * 100).toFixed(1)}%)`,
              ourProductDescription: `우리 제품에서 '${feature.name}'과 유사한 기능을 찾아보았습니다. 해당 기능의 구현 방식과 특징을 분석하여 경쟁력 있는 솔루션을 제공할 수 있는지 검토가 필요합니다.`,
              competitorLink: competitorUrl,
              ourProductLink: ourProductUrl,
            });
          }
          
          // 우리 제품 기능들 처리
          for (const feature of ourProductFeatures) {
            apiResults.push({
              feature: feature.name,
              competitor: 'X',
              ourProduct: 'O',
              competitorDescription: `경쟁사에서 '${feature.name}'과 유사한 기능을 찾아보았습니다. 해당 기능의 구현 방식과 특징을 분석하여 경쟁력 있는 솔루션을 제공할 수 있는지 검토가 필요합니다.`,
              ourProductDescription: `${feature.description} (신뢰도: ${(feature.confidence * 100).toFixed(1)}%)`,
              competitorLink: competitorUrl,
              ourProductLink: ourProductUrl,
            });
          }
          
          console.log("처리된 결과:", apiResults); // 디버깅용
        } else {
          setError(data.error || "통합 기능 탐지 중 오류가 발생했습니다.");
          return;
        }
      }

      setResults(apiResults);
    } catch (error: any) {
      console.error("분석 오류:", error);
      setError("분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleGetCrawlingResults = async () => {
    if (!competitorUrl.trim() || !ourProductUrl.trim()) {
      setError("URL을 먼저 입력해주세요.");
      return;
    }

    setLoadingCrawlingResults(true);
    try {
      const response = await autoDiscoveryAPI.getCrawlingResults(
        competitorUrl.trim(),
        ourProductUrl.trim()
      );

      if (response.data.success) {
        setCrawlingResults(response.data.data);
        setActiveTab(1); // 크롤링 결과 탭으로 이동
      } else {
        setError(response.data.error || "크롤링 결과 조회 중 오류가 발생했습니다.");
      }
    } catch (error: any) {
      console.error("크롤링 결과 조회 오류:", error);
      setError("크롤링 결과 조회 중 오류가 발생했습니다.");
    } finally {
      setLoadingCrawlingResults(false);
    }
  };



  const getStatusColor = (status: "O" | "X" | "△") => {
    switch (status) {
      case "O":
        return "success";
      case "X":
        return "error";
      case "△":
        return "warning";
      default:
        return "default";
    }
  };

  const getStatusText = (status: "O" | "X" | "△") => {
    switch (status) {
      case "O":
        return "지원";
      case "X":
        return "미지원";
      case "△":
        return "부분지원";
      default:
        return "";
    }
  };



  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        경쟁사 기능 분석
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "repeat(2, 1fr)" },
          gap: 3,
          mb: 3,
        }}
      >
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              경쟁사 제품 정보
            </Typography>
            <TextField
              fullWidth
              label="경쟁사 제품명"
              value={competitorName}
              onChange={(e) => setCompetitorName(e.target.value)}
              margin="normal"
              placeholder="예: Slack, Discord"
            />
            <TextField
              fullWidth
              label="경쟁사 도움말 URL"
              value={competitorUrl}
              onChange={(e) => setCompetitorUrl(e.target.value)}
              margin="normal"
              placeholder="https://help.slack.com"
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              우리 제품 정보
            </Typography>
            <TextField
              fullWidth
              label="우리 제품명"
              value={ourProductName}
              onChange={(e) => setOurProductName(e.target.value)}
              margin="normal"
              placeholder="예: 우리채팅"
            />
            <TextField
              fullWidth
              label="우리 제품 도움말 URL"
              value={ourProductUrl}
              onChange={(e) => setOurProductUrl(e.target.value)}
              margin="normal"
              placeholder="https://help.ourproduct.com"
            />
          </CardContent>
        </Card>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            분석 방식 선택
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            기능 목록을 직접 입력하거나 자동으로 기능을 발견하도록 선택할 수
            있습니다.
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Button
              variant={features.trim() ? "contained" : "outlined"}
              onClick={() => setFeatures("기능 목록을 입력하세요")}
              sx={{ mr: 1 }}
            >
              수동 입력
            </Button>
            <Button
              variant={!features.trim() ? "contained" : "outlined"}
              onClick={() => setFeatures("")}
            >
              자동 발견
            </Button>
          </Box>

          {features.trim() ? (
            <TextField
              fullWidth
              multiline
              rows={4}
              label="분석할 기능 목록"
              value={features}
              onChange={(e) => setFeatures(e.target.value)}
              placeholder="실시간 채팅, 파일 공유, 화상 회의, 모바일 앱, 데스크톱 앱, 봇 연동, API 제공"
            />
          ) : (
            <Alert severity="info">
              자동 기능 발견 모드: 두 도움말 페이지를 크롤링하여 유사한 기능들을
              자동으로 찾아 비교합니다.
            </Alert>
          )}
        </CardContent>
      </Card>

      <Box sx={{ mb: 3, display: "flex", gap: 2, flexWrap: "wrap" }}>
        <Button
          variant="contained"
          size="large"
          startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
          onClick={handleAnalyze}
          disabled={loading}
          sx={{ flex: 1, minWidth: 200 }}
        >
          {loading
            ? "분석 중..."
            : features.trim()
            ? "기능 분석 시작"
            : "자동 기능 발견 시작"}
        </Button>
        
        {!features.trim() && (
          <>
            <Button
              variant="outlined"
              size="large"
              startIcon={loadingCrawlingResults ? <CircularProgress size={20} /> : <VisibilityIcon />}
              onClick={handleGetCrawlingResults}
              disabled={loadingCrawlingResults}
            >
              실제 크롤링
            </Button>
          </>
        )}
      </Box>

      {/* 결과 탭 */}
      {(results.length > 0 || crawlingResults || vertexAIAnalysis) && (
        <Card>
          <CardContent>
            <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 2 }}>
              {results.length > 0 && (
                <Tab label={`분석 결과 (${results.length}개)`} />
              )}
              {vertexAIAnalysis && (
                <Tab label="Vertex AI 분석" />
              )}
              {crawlingResults && (
                <Tab label="크롤링 결과" />
              )}
            </Tabs>

            {/* 분석 결과 탭 */}
            {activeTab === 0 && results.length > 0 && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  {features.trim() ? "수동 기능 분석" : "자동 기능 발견 (Vertex AI)"} 모드로 분석되었습니다.
                </Alert>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>기능명</TableCell>
                        <TableCell align="center">
                          {competitorName || "경쟁사"}
                        </TableCell>
                        <TableCell align="center">
                          {ourProductName || "우리 제품"}
                        </TableCell>
                        <TableCell align="center">상세 정보</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {results.map((result, index) => (
                        <React.Fragment key={index}>
                          <TableRow>
                            <TableCell component="th" scope="row">
                              <Typography variant="subtitle1" fontWeight="bold">
                                {result.feature}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Box
                                sx={{
                                  color:
                                    getStatusColor(result.competitor) === "success"
                                      ? "green"
                                      : getStatusColor(result.competitor) === "error"
                                      ? "red"
                                      : "orange",
                                  fontWeight: "bold",
                                }}
                              >
                                {result.competitor} (
                                {getStatusText(result.competitor)})
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              <Box
                                sx={{
                                  color:
                                    getStatusColor(result.ourProduct) === "success"
                                      ? "green"
                                      : getStatusColor(result.ourProduct) === "error"
                                      ? "red"
                                      : "orange",
                                  fontWeight: "bold",
                                }}
                              >
                                {result.ourProduct} (
                                {getStatusText(result.ourProduct)})
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              <Button
                                size="small"
                                variant="outlined"
                                onClick={() => {
                                  setSelectedResult(result);
                                  setDetailModalOpen(true);
                                }}
                              >
                                상세보기
                              </Button>
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell colSpan={4} sx={{ py: 2 }}>
                              <Box sx={{ pl: 2 }}>
                                <Box sx={{ display: "flex", gap: 2, mb: 1 }}>
                                  <Typography variant="body2" color="text.secondary" sx={{ minWidth: 80 }}>
                                    경쟁사:
                                  </Typography>
                                  <Typography variant="body2" sx={{ flex: 1 }}>
                                    {result.competitorDescription || "설명 없음"}
                                  </Typography>
                                </Box>
                                <Box sx={{ display: "flex", gap: 2, mb: 1 }}>
                                  <Typography variant="body2" color="text.secondary" sx={{ minWidth: 80 }}>
                                    우리 제품:
                                  </Typography>
                                  <Typography variant="body2" sx={{ flex: 1 }}>
                                    {result.ourProductDescription || "설명 없음"}
                                  </Typography>
                                </Box>
                                <Box sx={{ display: "flex", gap: 2, mt: 1 }}>
                                  <Typography variant="body2" color="text.secondary" sx={{ minWidth: 80 }}>
                                    링크:
                                  </Typography>
                                  <Box sx={{ display: "flex", gap: 1 }}>
                                    {result.competitorLink && (
                                      <Button
                                        size="small"
                                        variant="outlined"
                                        href={result.competitorLink}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        sx={{ fontSize: '0.75rem' }}
                                      >
                                        경쟁사 도움말
                                      </Button>
                                    )}
                                    {result.ourProductLink && (
                                      <Button
                                        size="small"
                                        variant="outlined"
                                        href={result.ourProductLink}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        sx={{ fontSize: '0.75rem' }}
                                      >
                                        우리 제품 도움말
                                      </Button>
                                    )}
                                  </Box>
                                </Box>
                              </Box>
                            </TableCell>
                          </TableRow>
                        </React.Fragment>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}

            {/* Vertex AI 분석 탭 */}
            {activeTab === 1 && vertexAIAnalysis && (
              <Box>
                <Alert severity="success" sx={{ mb: 2 }}>
                  Vertex AI를 사용한 고급 기능 분석이 완료되었습니다.
                </Alert>
                
                {/* 경쟁사 기능 분석 */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    경쟁사 기능 분석
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      총 {vertexAIAnalysis.competitor_features.analysis_summary.total_features}개 기능 발견
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      주요 카테고리: {vertexAIAnalysis.competitor_features.analysis_summary.main_categories.join(', ')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      문서 품질: {vertexAIAnalysis.competitor_features.analysis_summary.document_quality}
                    </Typography>
                  </Box>
                  
                  {vertexAIAnalysis.competitor_features.extracted_features.map((feature, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, width: "100%" }}>
                          <Typography variant="subtitle1" sx={{ flex: 1 }}>
                            {feature.name}
                          </Typography>
                          <Chip label={feature.category} size="small" />
                          <Chip label={`${(feature.confidence * 100).toFixed(0)}%`} size="small" variant="outlined" />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {feature.description}
                        </Typography>
                        {feature.source_pages.length > 0 && (
                          <Box>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              출처 페이지:
                            </Typography>
                            {feature.source_pages.map((page, idx) => (
                              <Chip key={idx} label={page} size="small" variant="outlined" sx={{ mr: 1, mb: 1 }} />
                            ))}
                          </Box>
                        )}
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>

                {/* 우리 제품 기능 분석 */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    우리 제품 기능 분석
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      총 {vertexAIAnalysis.our_product_features.analysis_summary.total_features}개 기능 발견
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      주요 카테고리: {vertexAIAnalysis.our_product_features.analysis_summary.main_categories.join(', ')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      문서 품질: {vertexAIAnalysis.our_product_features.analysis_summary.document_quality}
                    </Typography>
                  </Box>
                  
                  {vertexAIAnalysis.our_product_features.extracted_features.map((feature, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, width: "100%" }}>
                          <Typography variant="subtitle1" sx={{ flex: 1 }}>
                            {feature.name}
                          </Typography>
                          <Chip label={feature.category} size="small" />
                          <Chip label={`${(feature.confidence * 100).toFixed(0)}%`} size="small" variant="outlined" />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {feature.description}
                        </Typography>
                        {feature.source_pages.length > 0 && (
                          <Box>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              출처 페이지:
                            </Typography>
                            {feature.source_pages.map((page, idx) => (
                              <Chip key={idx} label={page} size="small" variant="outlined" sx={{ mr: 1, mb: 1 }} />
                            ))}
                          </Box>
                        )}
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>

                {/* 기능 비교 분석 */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    기능 비교 분석
                  </Typography>
                  
                  {vertexAIAnalysis.comparison_analysis.feature_comparison.map((comparison, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, width: "100%" }}>
                          <Typography variant="subtitle1" sx={{ flex: 1 }}>
                            {comparison.feature_name}
                          </Typography>
                          <Chip 
                            label={comparison.priority} 
                            size="small" 
                            color={comparison.priority === 'high' ? 'error' : comparison.priority === 'medium' ? 'warning' : 'default'}
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            경쟁사 구현:
                          </Typography>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            {comparison.competitor_implementation}
                          </Typography>
                          
                          <Typography variant="subtitle2" gutterBottom>
                            우리 제품 구현:
                          </Typography>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            {comparison.our_implementation}
                          </Typography>
                          
                          <Typography variant="subtitle2" gutterBottom>
                            우리 제품의 장점:
                          </Typography>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            {comparison.advantage}
                          </Typography>
                          
                          <Typography variant="subtitle2" gutterBottom>
                            개선이 필요한 부분:
                          </Typography>
                          <Typography variant="body2">
                            {comparison.gap}
                          </Typography>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>

                {/* 경쟁력 분석 요약 */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    경쟁력 분석 요약
                  </Typography>
                  
                  <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2, mb: 3 }}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>
                          우리 제품의 강점
                        </Typography>
                        {vertexAIAnalysis.comparison_analysis.competitive_analysis.our_advantages.map((advantage, index) => (
                          <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                            • {advantage}
                          </Typography>
                        ))}
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>
                          경쟁사의 강점
                        </Typography>
                        {vertexAIAnalysis.comparison_analysis.competitive_analysis.competitor_advantages.map((advantage, index) => (
                          <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                            • {advantage}
                          </Typography>
                        ))}
                      </CardContent>
                    </Card>
                  </Box>
                  
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      시장에서 부족한 기능
                    </Typography>
                    {vertexAIAnalysis.comparison_analysis.competitive_analysis.market_gaps.map((gap, index) => (
                      <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                        • {gap}
                      </Typography>
                    ))}
                  </Box>
                  
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      개선 제안사항
                    </Typography>
                    {vertexAIAnalysis.comparison_analysis.competitive_analysis.recommendations.map((recommendation, index) => (
                      <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                        • {recommendation}
                      </Typography>
                    ))}
                  </Box>
                  
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        전체적인 경쟁력 평가
                      </Typography>
                      <Typography variant="body1">
                        {vertexAIAnalysis.comparison_analysis.summary.overall_assessment}
                      </Typography>
                      <Box sx={{ mt: 2, display: "flex", gap: 2 }}>
                        <Typography variant="body2">
                          비교 가능한 기능: {vertexAIAnalysis.comparison_analysis.summary.total_comparable_features}개
                        </Typography>
                        <Typography variant="body2">
                          우리만의 고유 기능: {vertexAIAnalysis.comparison_analysis.summary.our_unique_features}개
                        </Typography>
                        <Typography variant="body2">
                          경쟁사만의 고유 기능: {vertexAIAnalysis.comparison_analysis.summary.competitor_unique_features}개
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Box>
              </Box>
            )}

            {/* 크롤링 결과 탭 */}
            {activeTab === 2 && crawlingResults && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  크롤링된 원본 데이터입니다. 실제 크롤링된 텍스트 내용을 확인할 수 있습니다.
                </Alert>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    크롤링 통계
                  </Typography>
                  <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
                    <Chip 
                      label={`경쟁사: ${crawlingResults.competitor_features_count}개 기능`} 
                      color="primary" 
                      variant="outlined" 
                    />
                    <Chip 
                      label={`우리 제품: ${crawlingResults.our_product_features_count}개 기능`} 
                      color="secondary" 
                      variant="outlined" 
                    />
                    <Chip 
                      label={`상태: ${crawlingResults.crawling_status}`} 
                      color="info" 
                      variant="outlined" 
                    />
                  </Box>
                </Box>

                {/* 경쟁사 크롤링 결과 */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    경쟁사 크롤링 결과 ({crawlingResults.competitor_features.length}개)
                  </Typography>
                  {crawlingResults.competitor_features.map((feature, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, width: "100%" }}>
                          <Typography variant="subtitle1" sx={{ flex: 1 }}>
                            {feature.title}
                          </Typography>
                          {feature.category && (
                            <Chip label={feature.category} size="small" />
                          )}
                          {feature.granularity && (
                            <Chip label={feature.granularity} size="small" variant="outlined" />
                          )}
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            내용:
                          </Typography>
                          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                              {feature.content}
                            </Typography>
                          </Paper>
                        </Box>
                        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                          {feature.url && (
                            <Button
                              size="small"
                              variant="outlined"
                              href={feature.url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              원본 페이지
                            </Button>
                          )}
                          {feature.source_page_title && (
                            <Chip 
                              label={feature.source_page_title} 
                              size="small" 
                              variant="outlined" 
                            />
                          )}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>

                {/* 우리 제품 크롤링 결과 */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    우리 제품 크롤링 결과 ({crawlingResults.our_product_features.length}개)
                  </Typography>
                  {crawlingResults.our_product_features.map((feature, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, width: "100%" }}>
                          <Typography variant="subtitle1" sx={{ flex: 1 }}>
                            {feature.title}
                          </Typography>
                          {feature.category && (
                            <Chip label={feature.category} size="small" />
                          )}
                          {feature.granularity && (
                            <Chip label={feature.granularity} size="small" variant="outlined" />
                          )}
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            내용:
                          </Typography>
                          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                              {feature.content}
                            </Typography>
                          </Paper>
                        </Box>
                        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                          {feature.url && (
                            <Button
                              size="small"
                              variant="outlined"
                              href={feature.url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              원본 페이지
                            </Button>
                          )}
                          {feature.source_page_title && (
                            <Chip 
                              label={feature.source_page_title} 
                              size="small" 
                              variant="outlined" 
                            />
                          )}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      <Box sx={{ mt: 3, display: "flex", gap: 2 }}>
        <Button
          variant="outlined"
          onClick={() => navigate(`/projects/${projectId}`)}
        >
          프로젝트 상세로 돌아가기
        </Button>
      </Box>

      {/* 상세보기 모달 */}
      <Dialog
        open={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          기능 상세 분석: {selectedResult?.feature}
        </DialogTitle>
        <DialogContent>
          {selectedResult && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  경쟁사 분석
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                  <Typography variant="body1" sx={{ mr: 2 }}>
                    지원 상태:
                  </Typography>
                  <Box
                    sx={{
                      color:
                        getStatusColor(selectedResult.competitor) === "success"
                          ? "green"
                          : getStatusColor(selectedResult.competitor) === "error"
                          ? "red"
                          : "orange",
                      fontWeight: "bold",
                    }}
                  >
                    {selectedResult.competitor} ({getStatusText(selectedResult.competitor)})
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {selectedResult.competitorDescription || "설명 없음"}
                </Typography>
                {selectedResult.competitorLink && (
                  <Button
                    size="small"
                    variant="outlined"
                    href={selectedResult.competitorLink}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    경쟁사 도움말 보기
                  </Button>
                )}
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  우리 제품 분석
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                  <Typography variant="body1" sx={{ mr: 2 }}>
                    지원 상태:
                  </Typography>
                  <Box
                    sx={{
                      color:
                        getStatusColor(selectedResult.ourProduct) === "success"
                          ? "green"
                          : getStatusColor(selectedResult.ourProduct) === "error"
                          ? "red"
                          : "orange",
                      fontWeight: "bold",
                    }}
                  >
                    {selectedResult.ourProduct} ({getStatusText(selectedResult.ourProduct)})
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {selectedResult.ourProductDescription || "설명 없음"}
                </Typography>
                {selectedResult.ourProductLink && (
                  <Button
                    size="small"
                    variant="outlined"
                    href={selectedResult.ourProductLink}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    우리 제품 도움말 보기
                  </Button>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailModalOpen(false)}>닫기</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CrawlingPage;
