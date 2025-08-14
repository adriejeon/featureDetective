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
import { autoDiscoveryAPI, featureDetectionAPI } from "../services/api";

interface Product {
  name: string;
  url: string;
}

interface ExtractedFeature {
  name: string;
  description: string;
  confidence: number;
  source_pages?: string[];
}

interface AnalysisResult {
  feature: string;
  products: {
    [productName: string]: {
      status: "O" | "X" | "△";
      description?: string;
      link?: string;
      sourcePage?: string;
      confidence?: number;
      similarity?: number;
      features?: Array<{
        name: string;
        category: string;
        description: string;
        confidence: number;
        source_pages: string[];
        product_name: string;
      }>;
    };
  };
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

  const [products, setProducts] = React.useState<Product[]>([
    { name: "제품 1", url: "" },
    { name: "제품 2", url: "" },
    { name: "제품 3", url: "" },
  ]);
  const [features] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const [results, setResults] = React.useState<AnalysisResult[]>([]);
  const [selectedResult, setSelectedResult] =
    React.useState<AnalysisResult | null>(null);
  const [detailModalOpen, setDetailModalOpen] = React.useState(false);
  const [crawlingResults, setCrawlingResults] =
    React.useState<CrawlingResults | null>(null);
  const [vertexAIAnalysis] = React.useState<VertexAIAnalysis | null>(null);
  const [activeTab, setActiveTab] = React.useState(0);
  const [loadingCrawlingResults, setLoadingCrawlingResults] =
    React.useState(false);
  const [analysisSummary, setAnalysisSummary] = React.useState<any>(null);

  const updateProduct = (
    index: number,
    field: keyof Product,
    value: string
  ) => {
    const newProducts = [...products];
    newProducts[index] = { ...newProducts[index], [field]: value };
    setProducts(newProducts);
  };

  const addProduct = () => {
    setProducts([
      ...products,
      { name: `제품 ${products.length + 1}`, url: "" },
    ]);
  };

  const removeProduct = (index: number) => {
    if (products.length > 1) {
      const newProducts = products.filter((_, i) => i !== index);
      setProducts(newProducts);
    }
  };

  const handleAnalyze = async () => {
    setError("");

    // 최소 2개 이상의 제품이 입력되어야 함
    const validProducts = products.filter((p) => p.name.trim() && p.url.trim());
    if (validProducts.length < 2) {
      setError("최소 2개 이상의 제품 정보를 입력해주세요.");
      return;
    }

    setLoading(true);
    try {
      let apiResults: AnalysisResult[] = [];

      if (features.trim()) {
        // 수동 입력 모드 - 여러 제품 지원으로 변경 필요
        setError(
          "수동 입력 모드는 현재 여러 제품 비교를 지원하지 않습니다. 자동 기능 탐지를 사용해주세요."
        );
        return;
      } else {
        // 자동 발견 모드 (새로운 통합 기능 탐지 API 사용)
        console.log("다중 제품 기능 탐지 모드 시작");

        const validProducts = products.filter(
          (p) => p.name.trim() && p.url.trim()
        );
        const productUrls = validProducts.map((p) => p.url.trim());
        const projectName = `다중 제품 비교 - ${validProducts
          .map((p) => p.name)
          .join(", ")}`;

        const response = await featureDetectionAPI.detectFeatures(
          productUrls,
          [], // 우리 제품 URL은 비워둠 (모든 제품을 경쟁사로 취급)
          projectName
        );

        const data = response.data;
        console.log("다중 제품 기능 탐지 API 응답:", data);

        if (data.success) {
          console.log("API 응답 데이터:", data);

          // 상세 디버깅 로그 추가
          console.log("=== 상세 디버깅 정보 ===");
          console.log("분석 방법:", data.data.analysis_results.analysis_method);
          console.log(
            "경쟁사 기능 수:",
            data.data.analysis_results.competitor_features.extracted_features
              .length
          );
          console.log(
            "우리 제품 기능 수:",
            data.data.analysis_results.our_product_features.extracted_features
              .length
          );

          // 경쟁사 기능 상세 정보
          console.log("=== 경쟁사 기능 상세 ===");
          data.data.analysis_results.competitor_features.extracted_features.forEach(
            (feature: any, index: number) => {
              console.log(
                `${index + 1}. ${feature.name} (${feature.category})`
              );
              console.log(`   설명: ${feature.description}`);
              console.log(`   신뢰도: ${feature.confidence}`);
              console.log(`   제품명: ${feature.product_name}`);
              console.log(`   소스 페이지: ${feature.source_pages.join(", ")}`);
            }
          );

          // 우리 제품 기능 상세 정보
          console.log("=== 우리 제품 기능 상세 ===");
          data.data.analysis_results.our_product_features.extracted_features.forEach(
            (feature: any, index: number) => {
              console.log(
                `${index + 1}. ${feature.name} (${feature.category})`
              );
              console.log(`   설명: ${feature.description}`);
              console.log(`   신뢰도: ${feature.confidence}`);
              console.log(`   제품명: ${feature.product_name}`);
              console.log(`   소스 페이지: ${feature.source_pages.join(", ")}`);
            }
          );

          // 크롤링 결과 확인
          console.log("=== 크롤링 결과 확인 ===");
          console.log(
            "제품1 URL:",
            data.data.crawling_results.product_data.제품1?.url
          );
          console.log(
            "제품2 URL:",
            data.data.crawling_results.product_data.제품2?.url
          );
          console.log(
            "제품1 크롤링 페이지 수:",
            data.data.crawling_results.product_data.제품1?.data?.length
          );
          console.log(
            "제품2 크롤링 페이지 수:",
            data.data.crawling_results.product_data.제품2?.data?.length
          );

          // 입력된 URL과 실제 크롤링된 URL 비교
          console.log("=== URL 비교 ===");
          console.log("입력된 경쟁사 URL:", validProducts[0]?.url);
          console.log("입력된 우리 제품 URL:", validProducts[1]?.url);
          console.log(
            "실제 크롤링된 제품1 URL:",
            data.data.crawling_results.product_data.제품1?.url
          );
          console.log(
            "실제 크롤링된 제품2 URL:",
            data.data.crawling_results.product_data.제품2?.url
          );

          // 제품별 크롤링 데이터 샘플
          if (data.data.crawling_results.product_data.제품1?.data) {
            console.log("=== 제품1 크롤링 데이터 샘플 ===");
            data.data.crawling_results.product_data.제품1.data
              .slice(0, 3)
              .forEach((page: any, index: number) => {
                console.log(`${index + 1}. ${page.title}`);
                console.log(`   URL: ${page.url}`);
                console.log(`   내용: ${page.content.substring(0, 100)}...`);
              });
          }

          if (data.data.crawling_results.product_data.제품2?.data) {
            console.log("=== 제품2 크롤링 데이터 샘플 ===");
            data.data.crawling_results.product_data.제품2.data
              .slice(0, 3)
              .forEach((page: any, index: number) => {
                console.log(`${index + 1}. ${page.title}`);
                console.log(`   URL: ${page.url}`);
                console.log(`   내용: ${page.content.substring(0, 100)}...`);
              });
          }

          // 다중 제품 분석 결과 처리
          const analysisResults = data.data.analysis_results;
          const competitorFeatures =
            analysisResults.competitor_features?.extracted_features || [];
          const ourProductFeatures =
            analysisResults.our_product_features?.extracted_features || [];

          // 요약 정보 저장
          setAnalysisSummary({
            comparison_summary:
              analysisResults.comparison_analysis?.comparison_summary,
            competitive_analysis:
              analysisResults.comparison_analysis?.competitive_analysis,
            project_info: data.data.project_info,
            summary: data.data.summary,
            competitor_analysis:
              analysisResults.competitor_features?.analysis_summary,
            our_product_analysis:
              analysisResults.our_product_features?.analysis_summary,
            competitor_features: competitorFeatures,
            our_product_features: ourProductFeatures,
            competitor_product_analysis:
              analysisResults.competitor_features?.product_analysis,
            our_product_product_analysis:
              analysisResults.our_product_features?.product_analysis,
          });

          // 각 제품의 기능 목록을 그대로 표시
          apiResults = [];

          // 제품1 (competitor_features) 기능 목록
          if (competitorFeatures.length > 0) {
            apiResults.push({
              feature: "제품1 기능 목록",
              products: {
                제품1: {
                  status: "O",
                  description: `총 ${competitorFeatures.length}개 기능 발견`,
                  link: validProducts[0]?.url || "",
                  sourcePage: validProducts[0]?.url || "",
                  confidence: 1.0,
                  similarity: 1.0,
                  features: competitorFeatures,
                },
              },
            });
          } else {
            // 기능이 없을 때도 표시
            apiResults.push({
              feature: "제품1 기능 목록",
              products: {
                제품1: {
                  status: "X",
                  description:
                    "기능을 찾을 수 없습니다. (AI 분석 중 오류가 발생했을 수 있습니다)",
                  link: validProducts[0]?.url || "",
                  sourcePage: validProducts[0]?.url || "",
                  confidence: 0,
                  similarity: 0,
                  features: [],
                },
              },
            });
          }

          // 제품2 (our_product_features) 기능 목록
          if (ourProductFeatures.length > 0) {
            apiResults.push({
              feature: "제품2 기능 목록",
              products: {
                제품2: {
                  status: "O",
                  description: `총 ${ourProductFeatures.length}개 기능 발견`,
                  link: validProducts[1]?.url || "",
                  sourcePage: validProducts[1]?.url || "",
                  confidence: 1.0,
                  similarity: 1.0,
                  features: ourProductFeatures,
                },
              },
            });
          } else {
            // 기능이 없을 때도 표시
            apiResults.push({
              feature: "제품2 기능 목록",
              products: {
                제품2: {
                  status: "X",
                  description:
                    "기능을 찾을 수 없습니다. (AI 분석 중 오류가 발생했을 수 있습니다)",
                  link: validProducts[1]?.url || "",
                  sourcePage: validProducts[1]?.url || "",
                  confidence: 0,
                  similarity: 0,
                  features: [],
                },
              },
            });
          }

          console.log("처리된 결과:", apiResults);
        } else {
          setError(data.error || "다중 제품 기능 탐지 중 오류가 발생했습니다.");
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
    const validProducts = products.filter((p) => p.name.trim() && p.url.trim());
    if (validProducts.length < 2) {
      setError("최소 2개 이상의 제품 정보를 입력해주세요.");
      return;
    }

    setLoadingCrawlingResults(true);
    try {
      // 현재는 첫 번째와 두 번째 제품만 비교 (API 수정 필요)
      const response = await autoDiscoveryAPI.getCrawlingResults(
        validProducts[0].url.trim(),
        validProducts[1].url.trim()
      );

      if (response.data.success) {
        setCrawlingResults(response.data.data);
        setActiveTab(1); // 크롤링 결과 탭으로 이동
      } else {
        setError(
          response.data.error || "크롤링 결과 조회 중 오류가 발생했습니다."
        );
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

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h6" gutterBottom>
              제품 정보 입력
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={addProduct}
              disabled={products.length >= 5}
            >
              제품 추가
            </Button>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            비교할 제품들의 도움말 URL을 입력해주세요. 최소 2개 이상의 제품이
            필요합니다.
          </Typography>

          {products.map((product, index) => (
            <Box
              key={index}
              sx={{
                mb: 2,
                p: 2,
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 1,
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 1,
                }}
              >
                <Typography variant="subtitle2">{product.name}</Typography>
                {products.length > 1 && (
                  <Button
                    size="small"
                    color="error"
                    onClick={() => removeProduct(index)}
                  >
                    삭제
                  </Button>
                )}
              </Box>
              <Box
                sx={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 2 }}
              >
                <TextField
                  fullWidth
                  label="제품명"
                  value={product.name}
                  onChange={(e) => updateProduct(index, "name", e.target.value)}
                  size="small"
                  placeholder="예: Slack"
                />
                <TextField
                  fullWidth
                  label="도움말 URL"
                  value={product.url}
                  onChange={(e) => updateProduct(index, "url", e.target.value)}
                  size="small"
                  placeholder="https://help.slack.com"
                />
              </Box>
            </Box>
          ))}
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            분석 방식 선택
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Vertex AI를 사용하여 여러 제품의 도움말 페이지를 크롤링하고 기능을
            자동으로 분석합니다.
          </Typography>

          <Alert severity="info">
            자동 기능 탐지 모드: 입력한 제품들의 도움말 페이지를 크롤링하여
            유사한 기능들을 자동으로 찾아 비교합니다. Vertex AI가 각 제품의
            기능을 분석하고 요약해드립니다.
          </Alert>
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
          {loading ? "분석 중..." : "다중 제품 기능 분석 시작"}
        </Button>

        {!features.trim() && (
          <>
            <Button
              variant="outlined"
              size="large"
              startIcon={
                loadingCrawlingResults ? (
                  <CircularProgress size={20} />
                ) : (
                  <VisibilityIcon />
                )
              }
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
            <Tabs
              value={activeTab}
              onChange={(e, newValue) => setActiveTab(newValue)}
              sx={{ mb: 2 }}
            >
              {results.length > 0 && (
                <Tab label={`분석 결과 (${results.length}개)`} />
              )}
              {vertexAIAnalysis && <Tab label="Vertex AI 분석" />}
              {crawlingResults && <Tab label="크롤링 결과" />}
            </Tabs>

            {/* 분석 결과 탭 */}
            {activeTab === 0 && results.length > 0 && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  다중 제품 기능 분석 (Vertex AI) 모드로 분석되었습니다.
                </Alert>

                {/* 요약 정보 표시 */}
                {analysisSummary && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      분석 요약
                    </Typography>
                    <Box
                      sx={{
                        display: "grid",
                        gridTemplateColumns: {
                          xs: "1fr",
                          sm: "repeat(2, 1fr)",
                          md: "repeat(4, 1fr)",
                        },
                        gap: 2,
                        mb: 2,
                      }}
                    >
                      {analysisSummary.comparison_summary && (
                        <>
                          <Card sx={{ p: 2, textAlign: "center" }}>
                            <Typography variant="h4" color="primary">
                              {
                                analysisSummary.comparison_summary
                                  .common_features
                              }
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              공통 기능
                            </Typography>
                          </Card>
                          <Card sx={{ p: 2, textAlign: "center" }}>
                            <Typography variant="h4" color="success.main">
                              {
                                analysisSummary.comparison_summary
                                  .total_features_product1
                              }
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              제품1 총 기능
                            </Typography>
                          </Card>
                          <Card sx={{ p: 2, textAlign: "center" }}>
                            <Typography variant="h4" color="secondary.main">
                              {
                                analysisSummary.comparison_summary
                                  .total_features_product2
                              }
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              제품2 총 기능
                            </Typography>
                          </Card>
                          <Card sx={{ p: 2, textAlign: "center" }}>
                            <Typography variant="h4" color="info.main">
                              {results.length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              분석된 기능
                            </Typography>
                          </Card>
                        </>
                      )}
                    </Box>

                    {/* 제품 분석 결과 */}
                    <Card sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          AI 제품 분석 결과
                        </Typography>

                        {/* 제품1 분석 */}
                        {analysisSummary.competitor_analysis && (
                          <Box sx={{ mb: 3 }}>
                            <Typography
                              variant="h6"
                              color="primary"
                              gutterBottom
                            >
                              제품1 분석
                            </Typography>
                            <Box
                              sx={{
                                display: "flex",
                                gap: 2,
                                mb: 2,
                                flexWrap: "wrap",
                              }}
                            >
                              <Chip
                                label={`총 ${analysisSummary.competitor_analysis.total_features}개 기능`}
                                color="primary"
                                variant="outlined"
                              />
                              <Chip
                                label={`문서 품질: ${analysisSummary.competitor_analysis.document_quality}`}
                                color="success"
                                variant="outlined"
                              />
                              {analysisSummary.competitor_analysis.main_categories?.map(
                                (category: string, index: number) => (
                                  <Chip
                                    key={index}
                                    label={`주요 카테고리: ${category}`}
                                    color="secondary"
                                    variant="outlined"
                                  />
                                )
                              )}
                            </Box>
                            {/* AI 제품 분석 결과 */}
                            {analysisSummary.competitor_product_analysis && (
                              <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                  <strong>AI 제품 분석 결과:</strong>
                                </Typography>

                                {analysisSummary.competitor_product_analysis
                                  .product_characteristics && (
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>제품 유형:</strong>{" "}
                                      {
                                        analysisSummary
                                          .competitor_product_analysis
                                          .product_characteristics.product_type
                                      }
                                    </Typography>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>타겟 사용자:</strong>{" "}
                                      {
                                        analysisSummary
                                          .competitor_product_analysis
                                          .product_characteristics
                                          .target_audience
                                      }
                                    </Typography>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>핵심 가치:</strong>{" "}
                                      {
                                        analysisSummary
                                          .competitor_product_analysis
                                          .product_characteristics
                                          .core_value_proposition
                                      }
                                    </Typography>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>주요 강점:</strong>
                                    </Typography>
                                    <Box sx={{ pl: 2 }}>
                                      {analysisSummary.competitor_product_analysis.product_characteristics.key_strengths?.map(
                                        (strength: string, index: number) => (
                                          <Typography
                                            key={index}
                                            variant="body2"
                                            color="text.secondary"
                                            sx={{ mb: 0.5 }}
                                          >
                                            • {strength}
                                          </Typography>
                                        )
                                      )}
                                    </Box>
                                  </Box>
                                )}

                                {analysisSummary.competitor_product_analysis
                                  .feature_analysis && (
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>가장 중요한 기능:</strong>
                                    </Typography>
                                    <Box sx={{ pl: 2 }}>
                                      {analysisSummary.competitor_product_analysis.feature_analysis.most_important_features?.map(
                                        (feature: string, index: number) => (
                                          <Typography
                                            key={index}
                                            variant="body2"
                                            color="text.secondary"
                                            sx={{ mb: 0.5 }}
                                          >
                                            • {feature}
                                          </Typography>
                                        )
                                      )}
                                    </Box>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>기능 강조 영역:</strong>{" "}
                                      {
                                        analysisSummary
                                          .competitor_product_analysis
                                          .feature_analysis
                                          .feature_categories_emphasis
                                      }
                                    </Typography>
                                  </Box>
                                )}
                              </Box>
                            )}

                            {/* 기존 요약 정보 */}
                            <Typography variant="body2" sx={{ mb: 2 }}>
                              <strong>기본 정보:</strong>{" "}
                              {analysisSummary.competitor_analysis.main_categories?.join(
                                ", "
                              )}{" "}
                              분야에 특화된 제품으로, 총{" "}
                              {
                                analysisSummary.competitor_analysis
                                  .total_features
                              }
                              개의 기능을 제공합니다. 문서 품질이{" "}
                              {
                                analysisSummary.competitor_analysis
                                  .document_quality
                              }{" "}
                              수준으로 상세한 기능 설명을 제공합니다.
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              <strong>주요 기능:</strong>
                            </Typography>
                            <Box sx={{ pl: 2 }}>
                              {analysisSummary.competitor_features?.map(
                                (feature: any, index: number) => (
                                  <Typography
                                    key={index}
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{ mb: 0.5 }}
                                  >
                                    • {feature.name} (신뢰도:{" "}
                                    {(feature.confidence * 100).toFixed(1)}%)
                                  </Typography>
                                )
                              )}
                            </Box>
                          </Box>
                        )}

                        {/* 제품2 분석 */}
                        {analysisSummary.our_product_analysis && (
                          <Box sx={{ mb: 3 }}>
                            <Typography
                              variant="h6"
                              color="secondary"
                              gutterBottom
                            >
                              제품2 분석
                            </Typography>
                            <Box
                              sx={{
                                display: "flex",
                                gap: 2,
                                mb: 2,
                                flexWrap: "wrap",
                              }}
                            >
                              <Chip
                                label={`총 ${analysisSummary.our_product_analysis.total_features}개 기능`}
                                color="secondary"
                                variant="outlined"
                              />
                              <Chip
                                label={`문서 품질: ${analysisSummary.our_product_analysis.document_quality}`}
                                color="success"
                                variant="outlined"
                              />
                              {analysisSummary.our_product_analysis.main_categories?.map(
                                (category: string, index: number) => (
                                  <Chip
                                    key={index}
                                    label={`주요 카테고리: ${category}`}
                                    color="primary"
                                    variant="outlined"
                                  />
                                )
                              )}
                            </Box>
                            {/* AI 제품 분석 결과 */}
                            {analysisSummary.our_product_product_analysis && (
                              <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                  <strong>AI 제품 분석 결과:</strong>
                                </Typography>

                                {analysisSummary.our_product_product_analysis
                                  .product_characteristics && (
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>제품 유형:</strong>{" "}
                                      {
                                        analysisSummary
                                          .our_product_product_analysis
                                          .product_characteristics.product_type
                                      }
                                    </Typography>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>타겟 사용자:</strong>{" "}
                                      {
                                        analysisSummary
                                          .our_product_product_analysis
                                          .product_characteristics
                                          .target_audience
                                      }
                                    </Typography>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>핵심 가치:</strong>{" "}
                                      {
                                        analysisSummary
                                          .our_product_product_analysis
                                          .product_characteristics
                                          .core_value_proposition
                                      }
                                    </Typography>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>주요 강점:</strong>
                                    </Typography>
                                    <Box sx={{ pl: 2 }}>
                                      {analysisSummary.our_product_product_analysis.product_characteristics.key_strengths?.map(
                                        (strength: string, index: number) => (
                                          <Typography
                                            key={index}
                                            variant="body2"
                                            color="text.secondary"
                                            sx={{ mb: 0.5 }}
                                          >
                                            • {strength}
                                          </Typography>
                                        )
                                      )}
                                    </Box>
                                  </Box>
                                )}

                                {analysisSummary.our_product_product_analysis
                                  .feature_analysis && (
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>가장 중요한 기능:</strong>
                                    </Typography>
                                    <Box sx={{ pl: 2 }}>
                                      {analysisSummary.our_product_product_analysis.feature_analysis.most_important_features?.map(
                                        (feature: string, index: number) => (
                                          <Typography
                                            key={index}
                                            variant="body2"
                                            color="text.secondary"
                                            sx={{ mb: 0.5 }}
                                          >
                                            • {feature}
                                          </Typography>
                                        )
                                      )}
                                    </Box>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>기능 강조 영역:</strong>{" "}
                                      {
                                        analysisSummary
                                          .our_product_product_analysis
                                          .feature_analysis
                                          .feature_categories_emphasis
                                      }
                                    </Typography>
                                  </Box>
                                )}
                              </Box>
                            )}

                            {/* 기존 요약 정보 */}
                            <Typography variant="body2" sx={{ mb: 2 }}>
                              <strong>기본 정보:</strong>{" "}
                              {analysisSummary.our_product_analysis.main_categories?.join(
                                ", "
                              )}{" "}
                              분야에 특화된 제품으로, 총{" "}
                              {
                                analysisSummary.our_product_analysis
                                  .total_features
                              }
                              개의 기능을 제공합니다. 문서 품질이{" "}
                              {
                                analysisSummary.our_product_analysis
                                  .document_quality
                              }{" "}
                              수준으로 상세한 기능 설명을 제공합니다.
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              <strong>주요 기능:</strong>
                            </Typography>
                            <Box sx={{ pl: 2 }}>
                              {analysisSummary.our_product_features?.map(
                                (feature: any, index: number) => (
                                  <Typography
                                    key={index}
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{ mb: 0.5 }}
                                  >
                                    • {feature.name} (신뢰도:{" "}
                                    {(feature.confidence * 100).toFixed(1)}%)
                                  </Typography>
                                )
                              )}
                            </Box>
                          </Box>
                        )}
                      </CardContent>
                    </Card>

                    {/* 경쟁 분석 결과 */}
                    {analysisSummary.competitive_analysis && (
                      <Card sx={{ mb: 2 }}>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            경쟁 분석 결과
                          </Typography>
                          {analysisSummary.competitive_analysis
                            .recommendations && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>
                                추천사항:
                              </Typography>
                              <ul>
                                {analysisSummary.competitive_analysis.recommendations.map(
                                  (rec: string, index: number) => (
                                    <li key={index}>
                                      <Typography variant="body2">
                                        {rec}
                                      </Typography>
                                    </li>
                                  )
                                )}
                              </ul>
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    )}
                  </Box>
                )}
                {/* 각 제품의 기능 목록 표시 */}
                {results.map((result, index) => {
                  const productName = Object.keys(result.products)[0];
                  const productResult = result.products[productName];

                  return (
                    <Card key={index} sx={{ mb: 3 }}>
                      <CardContent>
                        <Typography variant="h5" gutterBottom>
                          {productName} 기능 목록
                        </Typography>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 2 }}
                        >
                          {productResult?.description}
                        </Typography>

                        {productResult?.features && (
                          <Box>
                            {productResult.features.map(
                              (feature: any, featureIndex: number) => (
                                <Card key={featureIndex} sx={{ mb: 2, p: 2 }}>
                                  <Box
                                    sx={{
                                      display: "flex",
                                      justifyContent: "space-between",
                                      alignItems: "flex-start",
                                      mb: 1,
                                    }}
                                  >
                                    <Typography variant="h6" sx={{ flex: 1 }}>
                                      {feature.name}
                                    </Typography>
                                    <Chip
                                      label={feature.category}
                                      size="small"
                                      color="primary"
                                      variant="outlined"
                                    />
                                  </Box>
                                  <Typography variant="body2" sx={{ mb: 2 }}>
                                    {feature.description}
                                  </Typography>
                                  <Box
                                    sx={{
                                      display: "flex",
                                      justifyContent: "space-between",
                                      alignItems: "center",
                                    }}
                                  >
                                    <Box sx={{ display: "flex", gap: 2 }}>
                                      <Typography
                                        variant="caption"
                                        color="text.secondary"
                                      >
                                        신뢰도:{" "}
                                        {(feature.confidence * 100).toFixed(1)}%
                                      </Typography>
                                    </Box>
                                    {feature.source_pages &&
                                      feature.source_pages.length > 0 && (
                                        <Button
                                          size="small"
                                          variant="outlined"
                                          href={feature.source_pages[0]}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                        >
                                          도움말에서 기능 보기
                                        </Button>
                                      )}
                                  </Box>
                                </Card>
                              )
                            )}
                          </Box>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
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
                      총{" "}
                      {
                        vertexAIAnalysis.competitor_features.analysis_summary
                          .total_features
                      }
                      개 기능 발견
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      주요 카테고리:{" "}
                      {vertexAIAnalysis.competitor_features.analysis_summary.main_categories.join(
                        ", "
                      )}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      문서 품질:{" "}
                      {
                        vertexAIAnalysis.competitor_features.analysis_summary
                          .document_quality
                      }
                    </Typography>
                  </Box>

                  {vertexAIAnalysis.competitor_features.extracted_features.map(
                    (feature, index) => (
                      <Accordion key={index} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                              width: "100%",
                            }}
                          >
                            <Typography variant="subtitle1" sx={{ flex: 1 }}>
                              {feature.name}
                            </Typography>
                            <Chip label={feature.category} size="small" />
                            <Chip
                              label={`${(feature.confidence * 100).toFixed(
                                0
                              )}%`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            {feature.description}
                          </Typography>
                          {feature.source_pages.length > 0 && (
                            <Box>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                gutterBottom
                              >
                                출처 페이지:
                              </Typography>
                              {feature.source_pages.map((page, idx) => (
                                <Chip
                                  key={idx}
                                  label={page}
                                  size="small"
                                  variant="outlined"
                                  sx={{ mr: 1, mb: 1 }}
                                />
                              ))}
                            </Box>
                          )}
                        </AccordionDetails>
                      </Accordion>
                    )
                  )}
                </Box>

                {/* 우리 제품 기능 분석 */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    우리 제품 기능 분석
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      총{" "}
                      {
                        vertexAIAnalysis.our_product_features.analysis_summary
                          .total_features
                      }
                      개 기능 발견
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      주요 카테고리:{" "}
                      {vertexAIAnalysis.our_product_features.analysis_summary.main_categories.join(
                        ", "
                      )}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      문서 품질:{" "}
                      {
                        vertexAIAnalysis.our_product_features.analysis_summary
                          .document_quality
                      }
                    </Typography>
                  </Box>

                  {vertexAIAnalysis.our_product_features.extracted_features.map(
                    (feature, index) => (
                      <Accordion key={index} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                              width: "100%",
                            }}
                          >
                            <Typography variant="subtitle1" sx={{ flex: 1 }}>
                              {feature.name}
                            </Typography>
                            <Chip label={feature.category} size="small" />
                            <Chip
                              label={`${(feature.confidence * 100).toFixed(
                                0
                              )}%`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            {feature.description}
                          </Typography>
                          {feature.source_pages.length > 0 && (
                            <Box>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                gutterBottom
                              >
                                출처 페이지:
                              </Typography>
                              {feature.source_pages.map((page, idx) => (
                                <Chip
                                  key={idx}
                                  label={page}
                                  size="small"
                                  variant="outlined"
                                  sx={{ mr: 1, mb: 1 }}
                                />
                              ))}
                            </Box>
                          )}
                        </AccordionDetails>
                      </Accordion>
                    )
                  )}
                </Box>

                {/* 기능 비교 분석 */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    기능 비교 분석
                  </Typography>

                  {vertexAIAnalysis.comparison_analysis.feature_comparison.map(
                    (comparison, index) => (
                      <Accordion key={index} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                              width: "100%",
                            }}
                          >
                            <Typography variant="subtitle1" sx={{ flex: 1 }}>
                              {comparison.feature_name}
                            </Typography>
                            <Chip
                              label={comparison.priority}
                              size="small"
                              color={
                                comparison.priority === "high"
                                  ? "error"
                                  : comparison.priority === "medium"
                                  ? "warning"
                                  : "default"
                              }
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
                    )
                  )}
                </Box>

                {/* 경쟁력 분석 요약 */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    경쟁력 분석 요약
                  </Typography>

                  <Box
                    sx={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: 2,
                      mb: 3,
                    }}
                  >
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>
                          우리 제품의 강점
                        </Typography>
                        {vertexAIAnalysis.comparison_analysis.competitive_analysis.our_advantages.map(
                          (advantage, index) => (
                            <Typography
                              key={index}
                              variant="body2"
                              sx={{ mb: 1 }}
                            >
                              • {advantage}
                            </Typography>
                          )
                        )}
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>
                          경쟁사의 강점
                        </Typography>
                        {vertexAIAnalysis.comparison_analysis.competitive_analysis.competitor_advantages.map(
                          (advantage, index) => (
                            <Typography
                              key={index}
                              variant="body2"
                              sx={{ mb: 1 }}
                            >
                              • {advantage}
                            </Typography>
                          )
                        )}
                      </CardContent>
                    </Card>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      시장에서 부족한 기능
                    </Typography>
                    {vertexAIAnalysis.comparison_analysis.competitive_analysis.market_gaps.map(
                      (gap, index) => (
                        <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                          • {gap}
                        </Typography>
                      )
                    )}
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      개선 제안사항
                    </Typography>
                    {vertexAIAnalysis.comparison_analysis.competitive_analysis.recommendations.map(
                      (recommendation, index) => (
                        <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                          • {recommendation}
                        </Typography>
                      )
                    )}
                  </Box>

                  <Card>
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        전체적인 경쟁력 평가
                      </Typography>
                      <Typography variant="body1">
                        {
                          vertexAIAnalysis.comparison_analysis.summary
                            .overall_assessment
                        }
                      </Typography>
                      <Box sx={{ mt: 2, display: "flex", gap: 2 }}>
                        <Typography variant="body2">
                          비교 가능한 기능:{" "}
                          {
                            vertexAIAnalysis.comparison_analysis.summary
                              .total_comparable_features
                          }
                          개
                        </Typography>
                        <Typography variant="body2">
                          우리만의 고유 기능:{" "}
                          {
                            vertexAIAnalysis.comparison_analysis.summary
                              .our_unique_features
                          }
                          개
                        </Typography>
                        <Typography variant="body2">
                          경쟁사만의 고유 기능:{" "}
                          {
                            vertexAIAnalysis.comparison_analysis.summary
                              .competitor_unique_features
                          }
                          개
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
                  크롤링된 원본 데이터입니다. 실제 크롤링된 텍스트 내용을 확인할
                  수 있습니다.
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
                    경쟁사 크롤링 결과 (
                    {crawlingResults.competitor_features.length}개)
                  </Typography>
                  {crawlingResults.competitor_features.map((feature, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 1,
                            width: "100%",
                          }}
                        >
                          <Typography variant="subtitle1" sx={{ flex: 1 }}>
                            {feature.title}
                          </Typography>
                          {feature.category && (
                            <Chip label={feature.category} size="small" />
                          )}
                          {feature.granularity && (
                            <Chip
                              label={feature.granularity}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box sx={{ mb: 2 }}>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            gutterBottom
                          >
                            내용:
                          </Typography>
                          <Paper sx={{ p: 2, bgcolor: "grey.50" }}>
                            <Typography
                              variant="body2"
                              sx={{ whiteSpace: "pre-wrap" }}
                            >
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
                    우리 제품 크롤링 결과 (
                    {crawlingResults.our_product_features.length}개)
                  </Typography>
                  {crawlingResults.our_product_features.map(
                    (feature, index) => (
                      <Accordion key={index} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                              width: "100%",
                            }}
                          >
                            <Typography variant="subtitle1" sx={{ flex: 1 }}>
                              {feature.title}
                            </Typography>
                            {feature.category && (
                              <Chip label={feature.category} size="small" />
                            )}
                            {feature.granularity && (
                              <Chip
                                label={feature.granularity}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Box sx={{ mb: 2 }}>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              gutterBottom
                            >
                              내용:
                            </Typography>
                            <Paper sx={{ p: 2, bgcolor: "grey.50" }}>
                              <Typography
                                variant="body2"
                                sx={{ whiteSpace: "pre-wrap" }}
                              >
                                {feature.content}
                              </Typography>
                            </Paper>
                          </Box>
                          <Box
                            sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}
                          >
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
                    )
                  )}
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
        <DialogTitle>{selectedResult?.feature}</DialogTitle>
        <DialogContent>
          {selectedResult && (
            <Box sx={{ mt: 2 }}>
              {Object.entries(selectedResult.products).map(
                ([productName, productResult]) => (
                  <Box key={productName} sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      {productName} 기능 목록
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 2 }}
                    >
                      {productResult?.description}
                    </Typography>

                    {productResult?.features && (
                      <Box>
                        {productResult.features.map(
                          (feature: any, featureIndex: number) => (
                            <Card key={featureIndex} sx={{ mb: 2, p: 2 }}>
                              <Box
                                sx={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "flex-start",
                                  mb: 1,
                                }}
                              >
                                <Typography variant="h6" sx={{ flex: 1 }}>
                                  {feature.name}
                                </Typography>
                                <Chip
                                  label={feature.category}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                              </Box>
                              <Typography variant="body2" sx={{ mb: 2 }}>
                                {feature.description}
                              </Typography>
                              <Box
                                sx={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "center",
                                }}
                              >
                                <Box sx={{ display: "flex", gap: 2 }}>
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                  >
                                    신뢰도:{" "}
                                    {(feature.confidence * 100).toFixed(1)}%
                                  </Typography>
                                </Box>
                                {feature.source_pages &&
                                  feature.source_pages.length > 0 && (
                                    <Button
                                      size="small"
                                      variant="outlined"
                                      href={feature.source_pages[0]}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                    >
                                      도움말에서 기능 보기
                                    </Button>
                                  )}
                              </Box>
                            </Card>
                          )
                        )}
                      </Box>
                    )}
                  </Box>
                )
              )}
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
