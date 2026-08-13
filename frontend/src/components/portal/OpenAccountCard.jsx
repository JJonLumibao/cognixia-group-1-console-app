import { useState } from "react";
import { Box, Paper, Typography, TextField, Button, Alert, Stack, MenuItem } from "@mui/material";
import { motion } from "framer-motion";
import AddCardOutlinedIcon from "@mui/icons-material/AddCardOutlined";
import { createAccount } from "../../api/accounts";

const ACCOUNT_TYPES = ["Checking", "Savings"];
const CURRENCIES = ["USD", "EUR", "GBP", "JPY"];

const emptyForm = {
  accountType: "Checking",
  branchId: "",
  balance: "0",
  currency: "USD",
  minBalance: "100",
  overdraftLimit: "500",
};

export default function OpenAccountCard({ ownerId, onCreated, delay = 0.3 }) {
  const [form, setForm] = useState(emptyForm);
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
        currency: form.currency,
        min_balance: parseFloat(form.minBalance) || 0,
        overdraft_limit: parseFloat(form.overdraftLimit) || 0,
      });
      setStatus({ error: "", success: "Account opened." });
      setForm(emptyForm);
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
      <Stack direction="row" spacing={1.25} sx={{ alignItems: "center", mb: 0.5 }}>
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
        sx={{ mb: 2 }}
        slotProps={{ htmlInput: { step: "0.01", min: "0" } }}
        value={form.balance}
        onChange={(e) => setForm({ ...form, balance: e.target.value })}
      />

      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Currency
      </Typography>
      <TextField
        select
        fullWidth
        sx={{ mb: 2 }}
        value={form.currency}
        onChange={(e) => setForm({ ...form, currency: e.target.value })}
      >
        {CURRENCIES.map((code) => (
          <MenuItem key={code} value={code}>
            {code}
          </MenuItem>
        ))}
      </TextField>

      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Minimum Balance
      </Typography>
      <TextField
        type="number"
        fullWidth
        sx={{ mb: 2 }}
        helperText="Applies to Savings accounts."
        slotProps={{ htmlInput: { step: "0.01", min: "0" } }}
        value={form.minBalance}
        onChange={(e) => setForm({ ...form, minBalance: e.target.value })}
      />

      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Overdraft Limit
      </Typography>
      <TextField
        type="number"
        fullWidth
        helperText="Applies to Checking accounts."
        slotProps={{ htmlInput: { step: "0.01", min: "0" } }}
        value={form.overdraftLimit}
        onChange={(e) => setForm({ ...form, overdraftLimit: e.target.value })}
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
