import React from "react";
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { projectAPI } from "../services/api";

const NewProject: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!name.trim()) {
      setError("프로젝트 이름을 입력해주세요.");
      return;
    }

    setLoading(true);
    try {
      console.log("프로젝트 생성 요청 시작:", {
        name: name.trim(),
        description: description.trim(),
      });
      const response = await projectAPI.createProject(
        name.trim(),
        description.trim()
      );
      console.log("프로젝트 생성 성공:", response.data);
      navigate(`/projects/${response.data.project.id}`);
    } catch (error: any) {
      console.error("프로젝트 생성 에러:", error);
      console.error("에러 응답:", error.response);
      setError(error.response?.data?.error || "프로젝트 생성에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        새 프로젝트 생성
      </Typography>

      <Paper sx={{ p: 3, maxWidth: 600 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="프로젝트 이름"
            value={name}
            onChange={(e) => setName(e.target.value)}
            margin="normal"
            required
            disabled={loading}
          />
          <TextField
            fullWidth
            label="프로젝트 설명"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            margin="normal"
            multiline
            rows={4}
            disabled={loading}
          />
          <Box sx={{ mt: 3, display: "flex", gap: 2 }}>
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : "프로젝트 생성"}
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate("/projects")}
              disabled={loading}
            >
              취소
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default NewProject;
