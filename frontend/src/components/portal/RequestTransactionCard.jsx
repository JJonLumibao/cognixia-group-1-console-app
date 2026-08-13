import { useState } from "react";
import { Box, Paper, Typography, TextField, Button, Alert, Stack, MenuItem } from "@mui/material";
import { motion } from "framer-motion";
import RequestQuoteOutlinedIcon from "@mui/icons-material/RequestQuoteOutlined";
import { createTransactionRequest } from "../../api/transactions";

// Backend TransactionType enum values are exactly "Deposit" and "Withdrawal"
// (case-sensitive) — the "Withdraw" label here is just friendlier UI copy.
const REQUEST_TYPES = [
  { value: "Deposit", label: "Deposit" },
  { value: "Withdrawal", label: "Withdraw" },
];

export default function RequestTransactionCard({ delay = 0.2 }) {
  const [form, setForm] = useState({ requestType: "Deposit", accountId: "", amount: "" });
  const [status, setStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ error: "", success: "" });
    setSubmitting(true);
    try {
      const payload = {
        request_type: form.requestType,
        amount: parseFloat(form.amount),
        ...(form.requestType === "Deposit"
          ? { to_account_id: form.accountId }
          : { from_account_id: form.accountId }),
      };
      await createTransactionRequest(payload);
      setStatus({ error: "", success: "Request submitted — a teller will review it shortly." });
      setForm({ ...form, accountId: "", amount: "" });
    } catch (err) {
      setStatus({ error: err.response?.data?.detail || "Failed to submit request.", success: "" });
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
            bgcolor: "rgba(28,42,74,0.06)",
            color: "primary.main",
            display: "grid",
            placeItems: "center",
          }}
        >
          <RequestQuoteOutlinedIcon fontSize="small" />
        </Box>
        <Typography variant="h6">Request a Transaction</Typography>
      </Stack>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
        Deposits and withdrawals go through a teller for approval.
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
        Request Type
      </Typography>
      <TextField
        select
        fullWidth
        sx={{ mb: 2 }}
        value={form.requestType}
        onChange={(e) => setForm({ ...form, requestType: e.target.value })}
      >
        {REQUEST_TYPES.map((opt) => (
          <MenuItem key={opt.value} value={opt.value}>
            {opt.label}
          </MenuItem>
        ))}
      </TextField>

      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Account ID
      </Typography>
      <TextField
        fullWidth
        required
        sx={{ mb: 2 }}
        value={form.accountId}
        onChange={(e) => setForm({ ...form, accountId: e.target.value })}
      />

      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Amount
      </Typography>
      <TextField
        type="number"
        fullWidth
        required
        slotProps={{ htmlInput: { step: "0.01", min: "0.01" } }}
        value={form.amount}
        onChange={(e) => setForm({ ...form, amount: e.target.value })}
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
        {submitting ? "Submitting…" : "Submit Request"}
      </Button>
    </Paper>
  );
}
