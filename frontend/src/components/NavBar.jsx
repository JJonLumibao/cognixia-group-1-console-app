import { AppBar, Toolbar, Typography, Button, Box, Chip } from "@mui/material";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { STAFF_ROLES } from "../constants/roles";

export default function NavBar() {
  const { isAuthenticated, user, hasRole, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <AppBar position="static">
      <Toolbar sx={{ gap: 2 }}>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{ textDecoration: "none", color: "inherit", flexGrow: 0 }}
        >
          Bank Management System
        </Typography>

        <Box sx={{ flexGrow: 1, display: "flex", gap: 1 }}>
          {isAuthenticated && hasRole("CUSTOMER") && (
            <Button color="inherit" component={RouterLink} to="/portal">
              Customer Portal
            </Button>
          )}
          {isAuthenticated && hasRole(...STAFF_ROLES) && (
            <Button color="inherit" component={RouterLink} to="/dashboard">
              Manager Dashboard
            </Button>
          )}
        </Box>

        {isAuthenticated ? (
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
            <Chip
              size="small"
              label={user.roles.join(", ")}
              color="secondary"
              variant="outlined"
              sx={{ color: "inherit", borderColor: "rgba(255,255,255,0.5)" }}
            />
            <Typography variant="body2">{user.email}</Typography>
            <Button color="inherit" onClick={handleLogout}>
              Logout
            </Button>
          </Box>
        ) : (
          <Box sx={{ display: "flex", gap: 1 }}>
            <Button color="inherit" component={RouterLink} to="/login">
              Login
            </Button>
            <Button color="inherit" component={RouterLink} to="/register">
              Register
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
