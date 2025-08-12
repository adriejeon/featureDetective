import React, { useState, useEffect } from "react";
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Slider,
  Divider,
} from "@mui/material";
import {
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as SettingsIcon,
  Download as DownloadIcon,
  Info as InfoIcon,
} from "@mui/icons-material";
import { useParams, useNavigate } from "react-router-dom";
import { advancedCrawlingAPI } from "../services/api";

interface CrawlResult {
  id: number;
  url: string;
  title: string;
  depth: number;
  source: string;
  content_length: number;
  status: string;
  extraction_method: string;
  created_at: string;
}

interface CrawlConfig {
  max_pages: number;
  max_depth: number;
  rate_limit: number;
  include_patterns: string[];
  exclude_patterns: string[];
  css_exclude_selectors: string[];
  follow_subdomains: boolean;
  use_sitemap: boolean;
  respect_robots_txt: boolean;
}

interface ConfigTemplate {
  name: string;
  description: string;
  max_pages: number;
  max_depth: number;
  include_patterns: string[];
  exclude_patterns: string[];
  css_exclude_selectors: string[];
}

const AdvancedCrawlingPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  
  // projectId 디버깅
  console.log("AdvancedCrawlingPage - projectId:", id, "타입:", typeof id);

  // 크롤링 설정
  const [baseUrl, setBaseUrl] = useState("");
  const [crawlType, setCrawlType] = useState("help_center");
  const [customConfig, setCustomConfig] = useState<CrawlConfig>({
    max_pages: 50,
    max_depth: 3,
    rate_limit: 1.0,
    include_patterns: [],
    exclude_patterns: [],
    css_exclude_selectors: [],
    follow_subdomains: true,
    use_sitemap: true,
    respect_robots_txt: true,
  });

  // 상태 관리
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [results, setResults] = useState<CrawlResult[]>([]);
  const [configTemplates, setConfigTemplates] = useState<Record<string, ConfigTemplate>>({});

  // 설정 템플릿 로드
  useEffect(() => {
    loadConfigTemplates();
  }, []);

  const loadConfigTemplates = async () => {
    try {
      const response = await advancedCrawlingAPI.getConfigTemplates();
      if (response.data.success) {
        setConfigTemplates(response.data.data);
      }
    } catch (error) {
      console.error("설정 템플릿 로드 실패:", error);
    }
  };

  // 크롤링 타입 변경 시 설정 업데이트
  useEffect(() => {
    if (configTemplates[crawlType]) {
      const template = configTemplates[crawlType];
      setCustomConfig({
        max_pages: template.max_pages,
        max_depth: template.max_depth,
        rate_limit: 1.0,
        include_patterns: template.include_patterns,
        exclude_patterns: template.exclude_patterns,
        css_exclude_selectors: template.css_exclude_selectors,
        follow_subdomains: true,
        use_sitemap: true,
        respect_robots_txt: true,
      });
    }
  }, [crawlType, configTemplates]);

  const handleCrawl = async () => {
    if (!baseUrl.trim()) {
      setError("URL을 입력해주세요.");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      console.log("크롤링 시작:", { 
        projectId: id, 
        projectIdType: typeof id, 
        baseUrl, 
        crawlType 
      });
      let response;
      
      switch (crawlType) {
        case "help_center":
          const numericProjectId = id ? Number(id) : null;
          console.log("헬프 센터 크롤링 호출:", { 
            projectId: numericProjectId, 
            projectIdType: typeof numericProjectId,
            baseUrl 
          });
          console.log("전송할 데이터:", {
            project_id: numericProjectId,
            base_url: baseUrl
          });
          console.log("전송할 데이터 JSON:", JSON.stringify({
            project_id: numericProjectId,
            base_url: baseUrl
          }));
          
          if (!numericProjectId) {
            throw new Error("프로젝트 ID가 유효하지 않습니다.");
          }
          
          response = await advancedCrawlingAPI.crawlHelpCenter(numericProjectId, baseUrl);
          break;
        case "documentation":
          response = await advancedCrawlingAPI.crawlDocumentation(Number(id), baseUrl);
          break;
        case "custom":
          response = await advancedCrawlingAPI.crawlWithCustomSettings(
            Number(id),
            baseUrl,
            {
              include_patterns: customConfig.include_patterns,
              exclude_patterns: customConfig.exclude_patterns,
              css_exclude_selectors: customConfig.css_exclude_selectors,
              max_pages: customConfig.max_pages,
              max_depth: customConfig.max_depth,
            }
          );
          break;
        default:
          response = await advancedCrawlingAPI.crawlSiteAdvanced(Number(id), baseUrl);
      }

      if (response.data.success) {
        setSuccess(`${response.data.message} (${response.data.data.total_pages}개 페이지)`);
        // 결과 로드
        loadCrawlResults();
      } else {
        setError(response.data.error || "크롤링 중 오류가 발생했습니다.");
      }
    } catch (error: any) {
      console.error("크롤링 오류:", error);
      setError("크롤링 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const loadCrawlResults = async () => {
    try {
      const response = await advancedCrawlingAPI.getAdvancedCrawlingStatus(Number(id));
      if (response.data.success) {
        setResults(response.data.data.results);
      }
    } catch (error) {
      console.error("결과 로드 실패:", error);
    }
  };

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const response = await advancedCrawlingAPI.exportCrawlResults(Number(id), format);
      if (response.data.success) {
        setSuccess(`${format.toUpperCase()} 형식으로 내보내기가 완료되었습니다.`);
      }
    } catch (error) {
      setError("내보내기 중 오류가 발생했습니다.");
    }
  };

  const addPattern = (type: 'include' | 'exclude' | 'css', pattern: string) => {
    if (!pattern.trim()) return;
    
    const key = type === 'include' ? 'include_patterns' : 
                type === 'exclude' ? 'exclude_patterns' : 'css_exclude_selectors';
    
    setCustomConfig(prev => ({
      ...prev,
      [key]: [...prev[key], pattern.trim()]
    }));
  };

  const handlePatternInput = (type: 'include' | 'exclude' | 'css', event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter') {
      const target = event.target as HTMLInputElement;
      addPattern(type, target.value);
      target.value = ''; // 입력 필드 초기화
    }
  };

  const removePattern = (type: 'include' | 'exclude' | 'css', index: number) => {
    const key = type === 'include' ? 'include_patterns' : 
                type === 'exclude' ? 'exclude_patterns' : 'css_exclude_selectors';
    
    setCustomConfig(prev => ({
      ...prev,
      [key]: prev[key].filter((_, i) => i !== index)
    }));
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        고급 크롤링 (Intercom 스타일)
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        웹사이트의 모든 하위 페이지를 자동으로 탐색하고 크롤링합니다.
        링크 기반 탐색, URL 패턴 매칭, CSS 선택자 제어 등의 고급 기능을 제공합니다.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            기본 설정
          </Typography>
          
          <TextField
            fullWidth
            label="크롤링할 URL"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            placeholder="https://example.com/help"
            sx={{ mb: 2 }}
          />

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>크롤링 타입</InputLabel>
            <Select
              value={crawlType}
              onChange={(e) => setCrawlType(e.target.value)}
              label="크롤링 타입"
            >
              <MenuItem value="help_center">헬프 센터 전용</MenuItem>
              <MenuItem value="documentation">문서 사이트 전용</MenuItem>
              <MenuItem value="custom">사용자 정의 설정</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
            onClick={handleCrawl}
            disabled={loading || !baseUrl.trim()}
            fullWidth
          >
            {loading ? "크롤링 중..." : "크롤링 시작"}
          </Button>
        </CardContent>
      </Card>

      {crawlType === "custom" && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              사용자 정의 설정
            </Typography>

            <Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 2, mb: 3 }}>
              <TextField
                label="최대 페이지 수"
                type="number"
                value={customConfig.max_pages}
                onChange={(e) => setCustomConfig(prev => ({ ...prev, max_pages: Number(e.target.value) }))}
                inputProps={{ min: 1, max: 1000 }}
              />
              <TextField
                label="최대 깊이"
                type="number"
                value={customConfig.max_depth}
                onChange={(e) => setCustomConfig(prev => ({ ...prev, max_depth: Number(e.target.value) }))}
                inputProps={{ min: 1, max: 10 }}
              />
              <TextField
                label="요청 간격 (초)"
                type="number"
                value={customConfig.rate_limit}
                onChange={(e) => setCustomConfig(prev => ({ ...prev, rate_limit: Number(e.target.value) }))}
                inputProps={{ min: 0.1, max: 10, step: 0.1 }}
              />
            </Box>

            <FormControlLabel
              control={
                <Switch
                  checked={customConfig.follow_subdomains}
                  onChange={(e) => setCustomConfig(prev => ({ ...prev, follow_subdomains: e.target.checked }))}
                />
              }
              label="하위 도메인 탐색"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={customConfig.use_sitemap}
                  onChange={(e) => setCustomConfig(prev => ({ ...prev, use_sitemap: e.target.checked }))}
                />
              }
              label="Sitemap 사용"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={customConfig.respect_robots_txt}
                  onChange={(e) => setCustomConfig(prev => ({ ...prev, respect_robots_txt: e.target.checked }))}
                />
              }
              label="robots.txt 준수"
            />

            <Divider sx={{ my: 2 }} />

            {/* 포함 패턴 */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">포함할 URL 패턴</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ mb: 2 }}>
                  <TextField
                    label="새 패턴 추가"
                    placeholder="*/help/*, */docs/*"
                    onKeyDown={(e) => handlePatternInput('include', e)}
                    sx={{ mr: 1, minWidth: 300 }}
                  />
                  <Button onClick={() => addPattern('include', '*/help/*')} size="small">
                    헬프 센터
                  </Button>
                  <Button onClick={() => addPattern('include', '*/docs/*')} size="small">
                    문서
                  </Button>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {customConfig.include_patterns.map((pattern, index) => (
                    <Chip
                      key={index}
                      label={pattern}
                      onDelete={() => removePattern('include', index)}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>

            {/* 제외 패턴 */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">제외할 URL 패턴</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ mb: 2 }}>
                  <TextField
                    label="새 패턴 추가"
                    placeholder="*.pdf, mailto:"
                    onKeyDown={(e) => handlePatternInput('exclude', e)}
                    sx={{ mr: 1, minWidth: 300 }}
                  />
                  <Button onClick={() => addPattern('exclude', '*.pdf')} size="small">
                    PDF
                  </Button>
                  <Button onClick={() => addPattern('exclude', 'mailto:')} size="small">
                    이메일
                  </Button>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {customConfig.exclude_patterns.map((pattern, index) => (
                    <Chip
                      key={index}
                      label={pattern}
                      onDelete={() => removePattern('exclude', index)}
                      color="error"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>

            {/* CSS 제외 선택자 */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">제외할 CSS 선택자</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ mb: 2 }}>
                  <TextField
                    label="새 선택자 추가"
                    placeholder="nav, footer, .ads"
                    onKeyDown={(e) => handlePatternInput('css', e)}
                    sx={{ mr: 1, minWidth: 300 }}
                  />
                  <Button onClick={() => addPattern('css', 'nav')} size="small">
                    네비게이션
                  </Button>
                  <Button onClick={() => addPattern('css', 'footer')} size="small">
                    푸터
                  </Button>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {customConfig.css_exclude_selectors.map((selector, index) => (
                    <Chip
                      key={index}
                      label={selector}
                      onDelete={() => removePattern('css', index)}
                      color="warning"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>
      )}

      {/* 결과 섹션 */}
      {results.length > 0 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                크롤링 결과 ({results.length}개 페이지)
              </Typography>
              <Box>
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExport('json')}
                  sx={{ mr: 1 }}
                >
                  JSON 내보내기
                </Button>
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExport('csv')}
                >
                  CSV 내보내기
                </Button>
              </Box>
            </Box>

            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>제목</TableCell>
                    <TableCell>URL</TableCell>
                    <TableCell align="center">깊이</TableCell>
                    <TableCell align="center">소스</TableCell>
                    <TableCell align="center">콘텐츠 길이</TableCell>
                    <TableCell align="center">상태</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.map((result) => (
                    <TableRow key={result.id}>
                      <TableCell>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {result.title || '제목 없음'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Button
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          size="small"
                          sx={{ textTransform: 'none', maxWidth: 300 }}
                        >
                          {result.url}
                        </Button>
                      </TableCell>
                      <TableCell align="center">{result.depth}</TableCell>
                      <TableCell align="center">
                        <Chip
                          label={result.source}
                          size="small"
                          color={result.source === 'initial' ? 'primary' : 'default'}
                        />
                      </TableCell>
                      <TableCell align="center">{result.content_length.toLocaleString()}자</TableCell>
                      <TableCell align="center">
                        <Chip
                          label={result.status}
                          size="small"
                          color={result.status === 'completed' ? 'success' : 'error'}
                        />
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
          onClick={() => navigate(`/projects/${id}`)}
        >
          프로젝트 상세로 돌아가기
        </Button>
        <Button
          variant="outlined"
          onClick={() => navigate(`/projects/${id}/crawling`)}
        >
          기본 크롤링으로 이동
        </Button>
      </Box>
    </Box>
  );
};

export default AdvancedCrawlingPage;
