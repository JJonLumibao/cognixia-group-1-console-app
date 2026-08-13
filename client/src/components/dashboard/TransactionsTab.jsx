import { useEffect, useState } from "react";
import { Box, Paper, Typography, TextField, Button, Alert, Grid, MenuItem, IconButton, Tooltip, Chip } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlined";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import {
  depositMoney,
  withdrawMoney,
  getTransactionRequests,
  approveTransactionRequest,
  rejectTransactionRequest,
} from "../../api/transactions";

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

const STATUS_COLOR = { Pending: "warning", Approved: "success", Rejected: "default" };

function RequestsPanel() {
  const [requests, setRequests] = useState([]);
  const [error, setError] = useState("");
  const [actingId, setActingId] = useState("");

  const loadRequests = async () => {
    try {
      setRequests(await getTransactionRequests());
      setError("");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to load transaction requests. You may need a branch assigned to your account."
      );
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const handleDecision = async (request, approve) => {
    setActingId(request.id);
    try {
      await (approve ? approveTransactionRequest : rejectTransactionRequest)(request.id);
      await loadRequests();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update request.");
    } finally {
      setActingId("");
    }
  };

  const requestColumns = [
    { field: "id", headerName: "Request ID", flex: 1 },
    { field: "request_type", headerName: "Type", flex: 0.7 },
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
      field: "status",
      headerName: "Status",
      flex: 0.7,
      renderCell: (params) => (
        <Chip size="small" label={params.value} color={STATUS_COLOR[params.value] || "default"} />
      ),
    },
    {
      field: "actions",
      headerName: "Actions",
      flex: 0.8,
      sortable: false,
      filterable: false,
      renderCell: (params) =>
        params.row.status === "Pending" && (
          <Box>
            <Tooltip title="Approve">
              <IconButton
                size="small"
                color="success"
                disabled={actingId === params.row.id}
                onClick={() => handleDecision(params.row, true)}
              >
                <CheckCircleOutlineIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Reject">
              <IconButton
                size="small"
                color="error"
                disabled={actingId === params.row.id}
                onClick={() => handleDecision(params.row, false)}
              >
                <HighlightOffIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        ),
    },
  ];

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Transaction Requests
      </Typography>
      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Box sx={{ height: 360 }}>
        <DataGrid rows={requests} columns={requestColumns} disableRowSelectionOnClick />
      </Box>
    </Paper>
  );
}

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
    <Box>
      <RequestsPanel />

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              All Transactions
            </Typography>
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
    </Box>
  );
}
