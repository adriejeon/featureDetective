import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Fab,
  CircularProgress,
  Alert,
} from "@mui/material";
import {
  Add as AddIcon,
  Search as SearchIcon,
  Assessment as AssessmentIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { projectAPI } from "../services/api";

const ProjectList: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await projectAPI.getProjects();
      setProjects(response.data.projects);
    } catch (error) {
      console.error("프로젝트 조회 오류:", error);
      setError("프로젝트 목록을 불러오는데 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (projectId: number) => {
    if (window.confirm("정말로 이 프로젝트를 삭제하시겠습니까?")) {
      try {
        await projectAPI.deleteProject(projectId);
        fetchProjects(); // 목록 새로고침
      } catch (error) {
        console.error("프로젝트 삭제 오류:", error);
        setError("프로젝트 삭제에 실패했습니다.");
      }
    }
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" component="h1">
          프로젝트 목록
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate("/projects/new")}
        >
          새 프로젝트
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {projects.length === 0 ? (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "400px",
            textAlign: "center",
          }}
        >
          <AssessmentIcon
            sx={{ fontSize: 80, color: "text.secondary", mb: 2 }}
          />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            아직 프로젝트가 없습니다
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            첫 번째 경쟁사 분석 프로젝트를 생성해보세요
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate("/projects/new")}
          >
            새 프로젝트 생성
          </Button>
        </Box>
      ) : (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              sm: "repeat(2, 1fr)",
              md: "repeat(3, 1fr)",
            },
            gap: 3,
          }}
        >
          {projects.map((project) => (
            <Card
              key={project.id}
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component="h2" gutterBottom>
                  {project.name}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  {project.description || "설명 없음"}
                </Typography>

                <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h6" color="primary">
                      {project.keyword_count || 0}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      키워드
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h6" color="primary">
                      {project.crawling_count || 0}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      분석 URL
                    </Typography>
                  </Box>
                </Box>

                <Typography variant="caption" color="text.secondary">
                  생성일: {new Date(project.created_at).toLocaleDateString()}
                </Typography>
              </CardContent>

              <CardActions sx={{ justifyContent: "space-between", p: 2 }}>
                <Box>
                  <Button
                    size="small"
                    startIcon={<SearchIcon />}
                    onClick={() => navigate(`/projects/${project.id}/crawling`)}
                  >
                    크롤링
                  </Button>
                  <Button
                    size="small"
                    startIcon={<AssessmentIcon />}
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    상세보기
                  </Button>
                </Box>
                <Box>
                  <Button
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    수정
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={() => handleDeleteProject(project.id)}
                  >
                    삭제
                  </Button>
                </Box>
              </CardActions>
            </Card>
          ))}
        </Box>
      )}

      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: "fixed", bottom: 16, right: 16 }}
        onClick={() => navigate("/projects/new")}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default ProjectList;
