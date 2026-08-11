import { useEffect, useMemo, useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Grid,
  Alert,
  Chip,
  CircularProgress,
} from "@mui/material";
import { getAccounts } from "../api/accounts";
import { getTransactions, transferFunds } from "../api/transactions";

export default function CustomerPortalPage() {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [ownerFilter, setOwnerFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [transfer, setTransfer] = useState({ from_account_id: "", to_account_id: "", amount: "" });
  const [transferStatus, setTransferStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setLoadError("");
    try {
      const [accountsData, transactionsData] = await Promise.all([getAccounts(), getTransactions()]);
      setAccounts(accountsData);
      setTransactions(transactionsData);
    } catch (err) {
      setLoadError(err.response?.data?.detail || "Failed to load account data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const visibleAccounts = useMemo(() => {
    if (!ownerFilter.trim()) return accounts;
    return accounts.filter((a) => a.owner_id.toLowerCase().includes(ownerFilter.trim().toLowerCase()));
  }, [accounts, ownerFilter]);

  const accountIds = useMemo(() => new Set(visibleAccounts.map((a) => a.id)), [visibleAccounts]);

  const visibleTransactions = useMemo(() => {
    if (!ownerFilter.trim()) return transactions;
    return transactions.filter(
      (t) => accountIds.has(t.from_account_id) || accountIds.has(t.to_account_id)
    );
  }, [transactions, accountIds, ownerFilter]);

  const handleTransferSubmit = async (e) => {
    e.preventDefault();
    setTransferStatus({ error: "", success: "" });
    setSubmitting(true);
    try {
      await transferFunds({
        from_account_id: transfer.from_account_id,
        to_account_id: transfer.to_account_id,
        amount: parseFloat(transfer.amount),
      });
      setTransferStatus({ error: "", success: "Transfer completed." });
      setTransfer({ from_account_id: "", to_account_id: "", amount: "" });
      loadData();
    } catch (err) {
      setTransferStatus({ error: err.response?.data?.detail || "Transfer failed.", success: "" });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Customer Portal
      </Typography>

      {loadError && <Alert severity="error" sx={{ mb: 2 }}>{loadError}</Alert>}

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
              <Typography variant="h6">My Accounts</Typography>
              <TextField
                size="small"
                label="Filter by owner/customer ID"
                value={ownerFilter}
                onChange={(e) => setOwnerFilter(e.target.value)}
              />
            </Box>

            {loading ? (
              <CircularProgress size={24} />
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Account ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Branch</TableCell>
                    <TableCell align="right">Balance</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {visibleAccounts.map((a) => (
                    <TableRow key={a.id}>
                      <TableCell>{a.id}</TableCell>
                      <TableCell>{a.account_type}</TableCell>
                      <TableCell>{a.branch_id}</TableCell>
                      <TableCell align="right">${a.balance.toFixed(2)}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={a.active ? "Active" : "Inactive"}
                          color={a.active ? "success" : "default"}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                  {visibleAccounts.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        No accounts found.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </Paper>

          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Transaction History
            </Typography>
            {loading ? (
              <CircularProgress size={24} />
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>From</TableCell>
                    <TableCell>To</TableCell>
                    <TableCell align="right">Amount</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {visibleTransactions
                    .slice()
                    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                    .map((t) => (
                      <TableRow key={t.id}>
                        <TableCell>{new Date(t.timestamp).toLocaleString()}</TableCell>
                        <TableCell>{t.type}</TableCell>
                        <TableCell>{t.from_account_id || "-"}</TableCell>
                        <TableCell>{t.to_account_id || "-"}</TableCell>
                        <TableCell align="right">${t.amount.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  {visibleTransactions.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        No transactions found.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 5 }}>
          <Paper sx={{ p: 3 }} component="form" onSubmit={handleTransferSubmit}>
            <Typography variant="h6" gutterBottom>
              Transfer Money
            </Typography>

            {transferStatus.error && <Alert severity="error" sx={{ mb: 2 }}>{transferStatus.error}</Alert>}
            {transferStatus.success && <Alert severity="success" sx={{ mb: 2 }}>{transferStatus.success}</Alert>}

            <TextField
              label="From Account ID"
              fullWidth
              required
              margin="normal"
              value={transfer.from_account_id}
              onChange={(e) => setTransfer({ ...transfer, from_account_id: e.target.value })}
            />
            <TextField
              label="To Account ID"
              fullWidth
              required
              margin="normal"
              value={transfer.to_account_id}
              onChange={(e) => setTransfer({ ...transfer, to_account_id: e.target.value })}
            />
            <TextField
              label="Amount"
              type="number"
              fullWidth
              required
              margin="normal"
              inputProps={{ step: "0.01", min: "0.01" }}
              value={transfer.amount}
              onChange={(e) => setTransfer({ ...transfer, amount: e.target.value })}
            />

            <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={submitting}>
              {submitting ? "Processing..." : "Transfer"}
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
