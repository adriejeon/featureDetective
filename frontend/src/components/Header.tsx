import React from "react";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Dashboard as DashboardIcon,
  List as ListIcon,
  Add as AddIcon,
} from "@mui/icons-material";

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, cursor: "pointer" }}
          onClick={() => navigate("/")}
        >
          🔍 Feature Detective
        </Typography>

        <Box sx={{ display: "flex", gap: 1 }}>
          <Button
            color="inherit"
            startIcon={<DashboardIcon />}
            onClick={() => navigate("/")}
            sx={{
              backgroundColor: isActive("/")
                ? "rgba(255, 255, 255, 0.1)"
                : "transparent",
            }}
          >
            대시보드
          </Button>

          <Button
            color="inherit"
            startIcon={<ListIcon />}
            onClick={() => navigate("/projects")}
            sx={{
              backgroundColor: isActive("/projects")
                ? "rgba(255, 255, 255, 0.1)"
                : "transparent",
            }}
          >
            프로젝트
          </Button>

          <Button
            color="inherit"
            startIcon={<AddIcon />}
            onClick={() => navigate("/projects/new")}
            sx={{
              backgroundColor: isActive("/projects/new")
                ? "rgba(255, 255, 255, 0.1)"
                : "transparent",
            }}
          >
            새 프로젝트
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
