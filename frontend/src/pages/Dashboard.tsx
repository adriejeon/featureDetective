import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  CircularProgress,
} from "@mui/material";
import {
  Add as AddIcon,
  Search as SearchIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { projectAPI } from "../services/api";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalProjects: 0,
    totalUrls: 0,
    totalKeywords: 0,
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await projectAPI.getProjects();
      const projectsData = response.data.projects;
      setProjects(projectsData);

      // 통계 계산
      const totalKeywords = projectsData.reduce(
        (sum: number, project: any) => sum + (project.keyword_count || 0),
        0
      );
      const totalUrls = projectsData.reduce(
        (sum: number, project: any) => sum + (project.crawling_count || 0),
        0
      );

      setStats({
        totalProjects: projectsData.length,
        totalUrls,
        totalKeywords,
      });
    } catch (error) {
      console.error("프로젝트 조회 오류:", error);
    } finally {
      setLoading(false);
    }
  };

  const statsData = [
    {
      title: "총 프로젝트",
      value: stats.totalProjects.toString(),
      icon: <AssessmentIcon sx={{ fontSize: 40 }} />,
      color: "#1976d2",
    },
    {
      title: "분석된 URL",
      value: stats.totalUrls.toString(),
      icon: <SearchIcon sx={{ fontSize: 40 }} />,
      color: "#2e7d32",
    },
    {
      title: "키워드",
      value: stats.totalKeywords.toString(),
      icon: <TrendingUpIcon sx={{ fontSize: 40 }} />,
      color: "#ed6c02",
    },
  ];

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
      <Typography variant="h4" component="h1" gutterBottom>
        대시보드
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, 1fr)",
            md: "repeat(3, 1fr)",
          },
          gap: 3,
          mb: 4,
        }}
      >
        {statsData.map((stat, index) => (
          <Card key={index}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Box sx={{ color: stat.color, mr: 2 }}>{stat.icon}</Box>
                <Box>
                  <Typography variant="h4" component="div">
                    {stat.value}
                  </Typography>
                  <Typography color="text.secondary">{stat.title}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "repeat(2, 1fr)" },
          gap: 3,
        }}
      >
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            최근 프로젝트
          </Typography>
          {projects.length > 0 ? (
            <Box sx={{ mb: 2 }}>
              {projects.slice(0, 3).map((project) => (
                <Box
                  key={project.id}
                  sx={{
                    mb: 1,
                    p: 1,
                    border: "1px solid #e0e0e0",
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="subtitle1">{project.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {project.description || "설명 없음"}
                  </Typography>
                </Box>
              ))}
            </Box>
          ) : (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                아직 프로젝트가 없습니다.
              </Typography>
            </Box>
          )}
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate("/projects/new")}
          >
            새 프로젝트 생성
          </Button>
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            빠른 작업
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => navigate("/projects/new")}
            >
              새 프로젝트 생성
            </Button>
            <Button
              variant="outlined"
              startIcon={<SearchIcon />}
              onClick={() => navigate("/projects")}
            >
              프로젝트 목록 보기
            </Button>
            <Button
              variant="outlined"
              startIcon={<AssessmentIcon />}
              onClick={() => navigate("/projects")}
            >
              분석 결과 보기
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default Dashboard;
