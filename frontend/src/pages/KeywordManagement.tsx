import React from "react";
import {
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { keywordAPI, Keyword } from "../services/api";

const KeywordManagement: React.FC = () => {
  const { id } = useParams();
  const projectId = parseInt(id || "0");
  const [open, setOpen] = React.useState(false);
  const [editingKeyword, setEditingKeyword] = React.useState<Keyword | null>(
    null
  );
  const [keywords, setKeywords] = React.useState<Keyword[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");
  const [keywordText, setKeywordText] = React.useState("");
  const [category, setCategory] = React.useState("");

  React.useEffect(() => {
    if (projectId) {
      loadKeywords();
    }
  }, [projectId]);

  const loadKeywords = async () => {
    try {
      setLoading(true);
      const response = await keywordAPI.getKeywords(projectId);
      setKeywords(response.data.keywords);
    } catch (error: any) {
      setError(
        error.response?.data?.error || "키워드 목록을 불러오는데 실패했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAddKeyword = () => {
    setEditingKeyword(null);
    setKeywordText("");
    setCategory("");
    setOpen(true);
  };

  const handleEditKeyword = (keyword: Keyword) => {
    setEditingKeyword(keyword);
    setKeywordText(keyword.keyword);
    setCategory(keyword.category);
    setOpen(true);
  };

  const handleDeleteKeyword = async (id: number) => {
    try {
      await keywordAPI.deleteKeyword(id);
      await loadKeywords();
    } catch (error: any) {
      setError(error.response?.data?.error || "키워드 삭제에 실패했습니다.");
    }
  };

  const handleSave = async () => {
    if (!keywordText.trim()) {
      setError("키워드를 입력해주세요.");
      return;
    }

    try {
      if (editingKeyword) {
        await keywordAPI.updateKeyword(editingKeyword.id, {
          keyword: keywordText.trim(),
          category: category.trim(),
        });
      } else {
        await keywordAPI.createKeyword(
          projectId,
          keywordText.trim(),
          category.trim()
        );
      }
      await loadKeywords();
      setOpen(false);
      setError("");
    } catch (error: any) {
      setError(error.response?.data?.error || "키워드 저장에 실패했습니다.");
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
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" component="h1">
          키워드 관리
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddKeyword}
        >
          키워드 추가
        </Button>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>키워드</TableCell>
                <TableCell>카테고리</TableCell>
                <TableCell align="right">작업</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {keywords.map((keyword) => (
                <TableRow key={keyword.id}>
                  <TableCell>{keyword.keyword}</TableCell>
                  <TableCell>{keyword.category}</TableCell>
                  <TableCell align="right">
                    <IconButton onClick={() => handleEditKeyword(keyword)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteKeyword(keyword.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          {editingKeyword ? "키워드 수정" : "키워드 추가"}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="키워드"
            fullWidth
            variant="outlined"
            value={keywordText}
            onChange={(e) => setKeywordText(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="카테고리"
            fullWidth
            variant="outlined"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>취소</Button>
          <Button onClick={handleSave}>저장</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default KeywordManagement;
