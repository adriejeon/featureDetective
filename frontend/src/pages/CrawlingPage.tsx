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
} from "@mui/material";
import {
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";
import { useParams, useNavigate } from "react-router-dom";

interface AnalysisResult {
  feature: string;
  competitor: "O" | "X" | "△";
  ourProduct: "O" | "X" | "△";
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
          apiResults = data.data.results.map((result: any) => ({
            feature: result.feature,
            competitor: result.competitor.status,
            ourProduct: result.our_product.status,
          }));
        } else {
          setError(data.error || "분석 중 오류가 발생했습니다.");
          return;
        }
      } else {
        // 자동 발견 모드
        const response = await fetch(
          "http://127.0.0.1:5001/api/auto-discovery/discover",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              competitor_url: competitorUrl.trim(),
              our_product_url: ourProductUrl.trim(),
            }),
          }
        );

        const data = await response.json();

        if (data.success) {
          apiResults = data.data.results.map((result: any) => ({
            feature: result.feature_name,
            competitor: result.competitor.status,
            ourProduct: result.our_product.status,
          }));
        } else {
          setError(data.error || "자동 기능 발견 중 오류가 발생했습니다.");
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

      <Box sx={{ mb: 3 }}>
        <Button
          variant="contained"
          size="large"
          startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
          onClick={handleAnalyze}
          disabled={loading}
          fullWidth
        >
          {loading
            ? "분석 중..."
            : features.trim()
            ? "기능 분석 시작"
            : "자동 기능 발견 시작"}
        </Button>
      </Box>

      {results.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              분석 결과
            </Typography>
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
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.map((result, index) => (
                    <TableRow key={index}>
                      <TableCell component="th" scope="row">
                        {result.feature}
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
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
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
    </Box>
  );
};

export default CrawlingPage;
