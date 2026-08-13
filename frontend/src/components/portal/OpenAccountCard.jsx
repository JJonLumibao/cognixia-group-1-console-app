import { useState } from "react";
import { Box, Paper, Typography, TextField, Button, Alert, Stack, MenuItem } from "@mui/material";
import { motion } from "framer-motion";
import AddCardOutlinedIcon from "@mui/icons-material/AddCardOutlined";
import { createAccount } from "../../api/accounts";

const ACCOUNT_TYPES = ["Checking", "Savings"];

export default function OpenAccountCard({ ownerId, onCreated, delay = 0.3 }) {
  const [form, setForm] = useState({ accountType: "Checking", branchId: "", balance: "0" });
  const [status, setStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ error: "", success: "" });
    setSubmitting(true);
    try {
      await createAccount({
        owner_id: ownerId,
        account_type: form.accountType,
        branch_id: form.branchId,
        balance: parseFloat(form.balance) || 0,
      });
      setStatus({ error: "", success: "Account opened." });
      setForm({ accountType: "Checking", branchId: "", balance: "0" });
      onCreated?.();
    } catch (err) {
      setStatus({ error: err.response?.data?.detail || "Failed to open account.", success: "" });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Paper
      component={motion.form}
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.16, 1, 0.3, 1] }}
      sx={{ p: 3, mt: 3 }}
    >
      <Stack direction="row" alignItems="center" spacing={1.25} sx={{ mb: 0.5 }}>
        <Box
          sx={{
            width: 34,
            height: 34,
            borderRadius: "9px",
            bgcolor: "rgba(176,141,87,0.12)",
            color: "secondary.dark",
            display: "grid",
            placeItems: "center",
          }}
        >
          <AddCardOutlinedIcon fontSize="small" />
        </Box>
        <Typography variant="h6">Open a New Account</Typography>
      </Stack>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
        Opens in your name — it'll appear in My Accounts once created.
      </Typography>

      {status.error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {status.error}
        </Alert>
      )}
      {status.success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {status.success}
        </Alert>
      )}

      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Account Type
      </Typography>
      <TextField
        select
        fullWidth
        sx={{ mb: 2 }}
        value={form.accountType}
        onChange={(e) => setForm({ ...form, accountType: e.target.value })}
      >
        {ACCOUNT_TYPES.map((type) => (
          <MenuItem key={type} value={type}>
            {type}
          </MenuItem>
        ))}
      </TextField>

      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Branch ID
      </Typography>
      <TextField
        fullWidth
        required
        placeholder="e.g. BR001"
        sx={{ mb: 2 }}
        value={form.branchId}
        onChange={(e) => setForm({ ...form, branchId: e.target.value })}
      />

      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Opening Balance
      </Typography>
      <TextField
        type="number"
        fullWidth
        slotProps={{ htmlInput: { step: "0.01", min: "0" } }}
        value={form.balance}
        onChange={(e) => setForm({ ...form, balance: e.target.value })}
      />

      <Button
        type="submit"
        component={motion.button}
        whileTap={{ scale: 0.98 }}
        variant="contained"
        fullWidth
        size="large"
        sx={{ mt: 3 }}
        disabled={submitting}
      >
        {submitting ? "Opening…" : "Open Account"}
      </Button>
    </Paper>
  );
}
