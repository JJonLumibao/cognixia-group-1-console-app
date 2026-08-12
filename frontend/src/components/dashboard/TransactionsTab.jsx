import { useState } from "react";
import { Box, Paper, Typography, TextField, Button, Alert, Grid, MenuItem } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { depositMoney, withdrawMoney } from "../../api/transactions";

const columns = [
  { field: "id", headerName: "Transaction ID", flex: 1 },
  { field: "type", headerName: "Type", flex: 0.7 },
  { field: "from_account_id", headerName: "From Account", flex: 1 },
  { field: "to_account_id", headerName: "To Account", flex: 1 },
  {
    field: "amount",
    headerName: "Amount",
    flex: 0.7,
    type: "number",
    valueFormatter: (value) => `$${Number(value).toFixed(2)}`,
  },
  {
    field: "timestamp",
    headerName: "Timestamp",
    flex: 1,
    valueFormatter: (value) => (value ? new Date(value).toLocaleString() : ""),
  },
];

export default function TransactionsTab({ transactions, onRefresh }) {
  const [form, setForm] = useState({ mode: "deposit", account_id: "", amount: "" });
  const [status, setStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ error: "", success: "" });
    setSubmitting(true);
    try {
      const action = form.mode === "deposit" ? depositMoney : withdrawMoney;
      await action({ accountId: form.account_id, amount: parseFloat(form.amount) });
      setStatus({ error: "", success: `${form.mode === "deposit" ? "Deposit" : "Withdrawal"} completed.` });
      setForm({ ...form, account_id: "", amount: "" });
      onRefresh();
    } catch (err) {
      setStatus({ error: err.response?.data?.detail || "Transaction failed.", success: "" });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 8 }}>
        <Paper sx={{ p: 2 }}>
          <Box sx={{ height: 480 }}>
            <DataGrid rows={transactions} columns={columns} disableRowSelectionOnClick />
          </Box>
        </Paper>
      </Grid>

      <Grid size={{ xs: 12, md: 4 }}>
        <Paper sx={{ p: 3 }} component="form" onSubmit={handleSubmit}>
          <Typography variant="h6" gutterBottom>
            Deposit / Withdraw
          </Typography>

          {status.error && <Alert severity="error" sx={{ mb: 2 }}>{status.error}</Alert>}
          {status.success && <Alert severity="success" sx={{ mb: 2 }}>{status.success}</Alert>}

          <TextField
            select
            label="Action"
            fullWidth
            margin="normal"
            size="small"
            value={form.mode}
            onChange={(e) => setForm({ ...form, mode: e.target.value })}
          >
            <MenuItem value="deposit">Deposit</MenuItem>
            <MenuItem value="withdraw">Withdraw</MenuItem>
          </TextField>
          <TextField
            label="Account ID"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.account_id}
            onChange={(e) => setForm({ ...form, account_id: e.target.value })}
          />
          <TextField
            label="Amount"
            type="number"
            fullWidth
            required
            margin="normal"
            size="small"
            slotProps={{ htmlInput: { step: "0.01", min: "0.01" } }}
            value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
          />

          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={submitting}>
            {submitting ? "Processing..." : form.mode === "deposit" ? "Deposit" : "Withdraw"}
          </Button>
        </Paper>
      </Grid>
    </Grid>
  );
}
