import { useState } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  Link,
  MenuItem,
} from "@mui/material";
import { useAuth } from "../context/AuthContext";
import { ROLES, STAFF_ROLES } from "../constants/roles";

const ROLE_OPTIONS = Object.values(ROLES);

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "", role: ROLES.CUSTOMER });
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
    <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
      <Paper sx={{ p: 4, width: 380 }} component="form" onSubmit={handleSubmit}>
        <Typography variant="h5" gutterBottom>
          Create Account
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Account created! Redirecting...
          </Alert>
        )}

        <TextField
          label="Email"
          type="email"
          fullWidth
          required
          margin="normal"
          value={form.email}
          onChange={handleChange("email")}
        />
        <TextField
          label="Password"
          type="password"
          fullWidth
          required
          margin="normal"
          value={form.password}
          onChange={handleChange("password")}
        />
        <TextField
          select
          label="Role"
          fullWidth
          margin="normal"
          value={form.role}
          onChange={handleChange("role")}
        >
          {ROLE_OPTIONS.map((role) => (
            <MenuItem key={role} value={role}>
              {role.replace("_", " ")}
            </MenuItem>
          ))}
        </TextField>

        <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={submitting}>
          {submitting ? "Creating..." : "Register"}
        </Button>

        <Typography variant="body2" sx={{ mt: 2, textAlign: "center" }}>
          Already have an account? <Link component={RouterLink} to="/login">Sign in</Link>
        </Typography>
      </Paper>
    </Box>
  );
}
