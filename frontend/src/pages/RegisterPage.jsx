import { useState } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { Box, TextField, Button, Typography, Alert, Link, MenuItem } from "@mui/material";
import { motion } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import { ROLES, STAFF_ROLES } from "../constants/roles";
import AuthLayout from "../components/AuthLayout";

const ROLE_OPTIONS = Object.values(ROLES);

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "", role: ROLES.CUSTOMER, branchId: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const user = await register(form);
      setSuccess(true);
      const isStaff = user.roles.some((r) => STAFF_ROLES.includes(r));
      setTimeout(() => navigate(isStaff ? "/dashboard" : "/portal"), 800);
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout eyebrow="Get started" title="Create your account" subtitle="Set up access in under a minute.">
      <Box component="form" onSubmit={handleSubmit}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Account created! Redirecting…
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
          value={form.email}
          onChange={handleChange("email")}
        />

        <Typography variant="subtitle2" sx={{ mt: 2, mb: 0.5 }}>
          Password
        </Typography>
        <TextField
          type="password"
          fullWidth
          required
          placeholder="••••••••"
          value={form.password}
          onChange={handleChange("password")}
        />

        <Typography variant="subtitle2" sx={{ mt: 2, mb: 0.5 }}>
          Role
        </Typography>
        <TextField select fullWidth value={form.role} onChange={handleChange("role")}>
          {ROLE_OPTIONS.map((role) => (
            <MenuItem key={role} value={role}>
              {role.replace("_", " ")}
            </MenuItem>
          ))}
        </TextField>

        <Typography variant="subtitle2" sx={{ mt: 2, mb: 0.5 }}>
          Branch ID
        </Typography>
        <TextField
          fullWidth
          required
          placeholder="e.g. BR001"
          helperText="Ask your branch manager if you don't know your branch code."
          value={form.branchId}
          onChange={handleChange("branchId")}
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
          {submitting ? "Creating…" : "Create Account"}
        </Button>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 3, textAlign: "center" }}>
          Already have an account?{" "}
          <Link component={RouterLink} to="/login" underline="hover" sx={{ fontWeight: 600 }}>
            Sign in
          </Link>
        </Typography>
      </Box>
    </AuthLayout>
  );
}
