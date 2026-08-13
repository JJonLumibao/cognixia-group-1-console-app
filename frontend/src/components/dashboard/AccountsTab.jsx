import { useState } from "react";
import { Box, Paper, Typography, TextField, Button, Alert, Grid, MenuItem } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { createAccount } from "../../api/accounts";
import { formatCurrency } from "../../utils/currency";

const ACCOUNT_TYPES = ["Checking", "Savings"];
const CURRENCIES = ["USD", "EUR", "GBP", "JPY"];

const columns = [
  { field: "id", headerName: "Account ID", flex: 1 },
  { field: "owner_id", headerName: "Owner ID", flex: 1 },
  { field: "account_type", headerName: "Type", flex: 1 },
  { field: "branch_id", headerName: "Branch", flex: 1 },
  { field: "currency", headerName: "Currency", flex: 0.6 },
  {
    field: "balance",
    headerName: "Balance",
    flex: 1,
    type: "number",
    valueFormatter: (value, row) => formatCurrency(value, row.currency),
  },
  {
    field: "active",
    headerName: "Active",
    flex: 0.6,
    valueFormatter: (value) => (value ? "Yes" : "No"),
  },
];

export default function AccountsTab({ accounts, onFiltersChange, onRefresh }) {
  const [filters, setFilters] = useState({ branchId: "", minBalance: "" });
  const [form, setForm] = useState({
    owner_id: "",
    account_type: "Checking",
    balance: "0",
    currency: "USD",
    branch_id: "",
    min_balance: "100",
    overdraft_limit: "500",
  });
  const [status, setStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);

  const applyFilters = () => {
    onFiltersChange({
      branchId: filters.branchId || undefined,
      minBalance: filters.minBalance ? parseFloat(filters.minBalance) : undefined,
    });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setStatus({ error: "", success: "" });
    setSubmitting(true);
    try {
      await createAccount({
        owner_id: form.owner_id,
        account_type: form.account_type,
        balance: parseFloat(form.balance) || 0,
        currency: form.currency,
        branch_id: form.branch_id,
        min_balance: parseFloat(form.min_balance) || 0,
        overdraft_limit: parseFloat(form.overdraft_limit) || 0,
      });
      setStatus({ error: "", success: "Account created." });
      setForm({ ...form, owner_id: "", branch_id: "" });
      onRefresh();
    } catch (err) {
      setStatus({ error: err.response?.data?.detail || "Failed to create account.", success: "" });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 8 }}>
        <Paper sx={{ p: 2 }}>
          <Box sx={{ display: "flex", gap: 2, mb: 2, flexWrap: "wrap" }}>
            <TextField
              size="small"
              label="Branch ID"
              value={filters.branchId}
              onChange={(e) => setFilters({ ...filters, branchId: e.target.value })}
            />
            <TextField
              size="small"
              label="Min Balance"
              type="number"
              value={filters.minBalance}
              onChange={(e) => setFilters({ ...filters, minBalance: e.target.value })}
            />
            <Button variant="outlined" onClick={applyFilters}>
              Apply Filters
            </Button>
          </Box>
          <Box sx={{ height: 480 }}>
            <DataGrid rows={accounts} columns={columns} disableRowSelectionOnClick />
          </Box>
        </Paper>
      </Grid>

      <Grid size={{ xs: 12, md: 4 }}>
        <Paper sx={{ p: 3 }} component="form" onSubmit={handleCreate}>
          <Typography variant="h6" gutterBottom>
            Open New Account
          </Typography>

          {status.error && <Alert severity="error" sx={{ mb: 2 }}>{status.error}</Alert>}
          {status.success && <Alert severity="success" sx={{ mb: 2 }}>{status.success}</Alert>}

          <TextField
            label="Owner / Customer ID"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.owner_id}
            onChange={(e) => setForm({ ...form, owner_id: e.target.value })}
          />
          <TextField
            select
            label="Account Type"
            fullWidth
            margin="normal"
            size="small"
            value={form.account_type}
            onChange={(e) => setForm({ ...form, account_type: e.target.value })}
          >
            {ACCOUNT_TYPES.map((type) => (
              <MenuItem key={type} value={type}>
                {type}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Branch ID"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.branch_id}
            onChange={(e) => setForm({ ...form, branch_id: e.target.value })}
          />
          <TextField
            label="Opening Balance"
            type="number"
            fullWidth
            margin="normal"
            size="small"
            value={form.balance}
            onChange={(e) => setForm({ ...form, balance: e.target.value })}
          />
          <TextField
            select
            label="Currency"
            fullWidth
            margin="normal"
            size="small"
            value={form.currency}
            onChange={(e) => setForm({ ...form, currency: e.target.value })}
          >
            {CURRENCIES.map((code) => (
              <MenuItem key={code} value={code}>
                {code}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Min Balance"
            type="number"
            fullWidth
            margin="normal"
            size="small"
            value={form.min_balance}
            onChange={(e) => setForm({ ...form, min_balance: e.target.value })}
          />
          <TextField
            label="Overdraft Limit"
            type="number"
            fullWidth
            margin="normal"
            size="small"
            value={form.overdraft_limit}
            onChange={(e) => setForm({ ...form, overdraft_limit: e.target.value })}
          />

          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={submitting}>
            {submitting ? "Creating..." : "Create Account"}
          </Button>
        </Paper>
      </Grid>
    </Grid>
  );
}
