import { useEffect, useState } from "react";
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
import { transferFunds } from "../api/transactions";
import { getMyCustomer } from "../api/customers";

export default function CustomerPortalPage() {
  const [customer, setCustomer] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [noProfile, setNoProfile] = useState(false);

  const [transfer, setTransfer] = useState({ from_account_id: "", to_account_id: "", amount: "" });
  const [transferStatus, setTransferStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setLoadError("");
    setNoProfile(false);
    try {
      // GET /accounts is auto-filtered to the logged-in customer's own accounts.
      const accountsData = await getAccounts();
      setAccounts(accountsData);
    } catch (err) {
      if (err.response?.status === 404) {
        setNoProfile(true);
      } else {
        setLoadError(err.response?.data?.detail || "Failed to load account data.");
      }
    }

    try {
      setCustomer(await getMyCustomer());
    } catch {
      // No matching customer profile yet — accounts fetch above already surfaces this.
    }

    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

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

  if (!loading && noProfile) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Customer Portal
        </Typography>
        <Alert severity="warning">
          No customer profile is linked to your account yet. Ask a branch manager to add you as a
          customer using the same email you registered with.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Customer Portal{customer ? ` — Welcome, ${customer.name}` : ""}
      </Typography>

      {loadError && <Alert severity="error" sx={{ mb: 2 }}>{loadError}</Alert>}

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              My Accounts
            </Typography>

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
                  {accounts.map((a) => (
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
                  {accounts.length === 0 && (
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
        </Grid>

        <Grid size={{ xs: 12, md: 5 }}>
          <Paper sx={{ p: 3 }} component="form" onSubmit={handleTransferSubmit}>
            <Typography variant="h6" gutterBottom>
              Transfer Money
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              You can only transfer from an account you own.
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
              slotProps={{ htmlInput: { step: "0.01", min: "0.01" } }}
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
