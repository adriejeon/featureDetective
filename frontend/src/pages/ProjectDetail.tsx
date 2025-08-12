import React from "react";
import { Box, Typography, Paper, Button, Chip, Divider } from "@mui/material";
import { useParams, useNavigate } from "react-router-dom";

const ProjectDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // 임시 프로젝트 데이터
  const project = {
    id: 1,
    name: "경쟁사 기능 분석 프로젝트",
    description: "주요 경쟁사의 기능을 분석하여 자사 제품과 비교",
    keywordCount: 15,
    crawlingCount: 8,
    createdAt: "2024-01-15",
    status: "진행중",
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {project.name}
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "2fr 1fr" },
          gap: 3,
        }}
      >
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            프로젝트 정보
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {project.description}
          </Typography>
          <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
            <Chip label={project.status} color="primary" />
            <Chip label={`키워드 ${project.keywordCount}개`} />
            <Chip label={`크롤링 ${project.crawlingCount}개`} />
          </Box>
          <Typography variant="body2" color="text.secondary">
            생성일: {project.createdAt}
          </Typography>
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            빠른 작업
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Button
              variant="contained"
              onClick={() => navigate(`/projects/${id}/keywords`)}
            >
              키워드 관리
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate(`/projects/${id}/crawling`)}
            >
              기본 크롤링
            </Button>
            <Button
              variant="contained"
              onClick={() => navigate(`/projects/${id}/advanced-crawling`)}
            >
              고급 크롤링 (Intercom 스타일)
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate(`/projects/${id}/report`)}
            >
              리포트 생성
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default ProjectDetail;
