import { useState } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { Box, TextField, Button, Typography, Alert, Link } from "@mui/material";
import { motion } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import { STAFF_ROLES } from "../constants/roles";
import AuthLayout from "../components/AuthLayout";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const user = await login({ email, password });
      const isStaff = user.roles.some((r) => STAFF_ROLES.includes(r));
      navigate(isStaff ? "/dashboard" : "/portal");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout eyebrow="Welcome back" title="Sign in to your account" subtitle="Enter your credentials to continue.">
      <Box component="form" onSubmit={handleSubmit}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
          Email address
        </Typography>
        <TextField
          type="email"
          fullWidth
          required
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <Typography variant="subtitle2" sx={{ mt: 2, mb: 0.5 }}>
          Password
        </Typography>
        <TextField
          type="password"
          fullWidth
          required
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button
          type="submit"
          component={motion.button}
          whileTap={{ scale: 0.98 }}
          variant="contained"
          fullWidth
          size="large"
          sx={{ mt: 3.5 }}
          disabled={submitting}
        >
          {submitting ? "Signing in…" : "Sign In"}
        </Button>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 3, textAlign: "center" }}>
          Don't have an account?{" "}
          <Link component={RouterLink} to="/register" underline="hover" sx={{ fontWeight: 600 }}>
            Create one
          </Link>
        </Typography>
      </Box>
    </AuthLayout>
  );
}
