import { useEffect, useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  Chip,
  CircularProgress,
  Stack,
  Divider,
  IconButton,
  Tooltip,
} from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import SavingsOutlinedIcon from "@mui/icons-material/SavingsOutlined";
import CreditCardOutlinedIcon from "@mui/icons-material/CreditCardOutlined";
import SwapHorizOutlinedIcon from "@mui/icons-material/SwapHorizOutlined";
import ContentCopyOutlinedIcon from "@mui/icons-material/ContentCopyOutlined";
import { getAccounts, updateAccountStatus } from "../api/accounts";
import { transferFunds } from "../api/transactions";
import { getMyCustomer } from "../api/customers";
import AppShell from "../components/AppShell";
import AnimatedNumber from "../components/AnimatedNumber";
import RequestTransactionCard from "../components/portal/RequestTransactionCard";
import OpenAccountCard from "../components/portal/OpenAccountCard";

const listVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
};

const rowVariants = {
  hidden: { opacity: 0, x: -12 },
  show: { opacity: 1, x: 0, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] } },
};

function accountIcon(type) {
  return (type || "").toLowerCase().includes("saving") ? SavingsOutlinedIcon : CreditCardOutlinedIcon;
}

export default function CustomerPortalPage() {
  const [customer, setCustomer] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [noProfile, setNoProfile] = useState(false);

  const [transfer, setTransfer] = useState({ from_account_id: "", to_account_id: "", amount: "" });
  const [transferStatus, setTransferStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);
  const [copiedId, setCopiedId] = useState("");
  const [statusUpdatingId, setStatusUpdatingId] = useState("");

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

  const handleUseAsFrom = (accountId) => {
    setTransfer((prev) => ({ ...prev, from_account_id: accountId }));
  };

  const handleCopyId = async (e, accountId) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(accountId);
      setCopiedId(accountId);
      setTimeout(() => setCopiedId(""), 1500);
    } catch {
      // Clipboard access denied — nothing to do.
    }
  };

  const handleToggleStatus = async (e, account) => {
    e.stopPropagation();
    setStatusUpdatingId(account.id);
    try {
      await updateAccountStatus(account.id, !account.active);
      await loadData();
    } catch (err) {
      setTransferStatus({ error: err.response?.data?.detail || "Failed to update account status.", success: "" });
    } finally {
      setStatusUpdatingId("");
    }
  };

  const totalBalance = accounts.reduce((sum, a) => sum + a.balance, 0);

  if (!loading && noProfile) {
    return (
      <AppShell title="Customer Portal">
        <Alert severity="warning">
          No customer profile is linked to your account yet. Ask a branch manager to add you as a customer using
          the same email you registered with.
        </Alert>
      </AppShell>
    );
  }

  return (
    <AppShell
      title={customer ? `Welcome back, ${customer.name.split(" ")[0]}` : "Customer Portal"}
      subtitle="Here's what's happening with your accounts today."
    >
      {loadError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {loadError}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Paper
            component={motion.div}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            sx={{
              p: 3.5,
              mb: 3,
              background: "linear-gradient(135deg, #16213C, #0B1220)",
              color: "#fff",
              border: "none",
            }}
          >
            <Typography sx={{ fontSize: 12, letterSpacing: 1, color: "rgba(255,255,255,0.6)", mb: 0.5 }}>
              TOTAL BALANCE
            </Typography>
            {loading ? (
              <CircularProgress size={24} sx={{ color: "#fff" }} />
            ) : (
              <Typography sx={{ fontFamily: '"Lora", serif', fontWeight: 700, fontSize: 40 }}>
                <AnimatedNumber value={totalBalance} prefix="$" format={(v) => v.toFixed(2)} />
              </Typography>
            )}
            <Typography sx={{ fontSize: 13, color: "rgba(255,255,255,0.55)", mt: 0.5 }}>
              across {accounts.length} account{accounts.length === 1 ? "" : "s"}
            </Typography>
          </Paper>

          <Paper
            component={motion.div}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            sx={{ p: 3 }}
          >
            <Typography variant="h6" sx={{ mb: 0.25 }}>
              My Accounts
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Click an account to use it as the sender in a transfer, or use the recipient button.
            </Typography>

            {loading ? (
              <CircularProgress size={24} />
            ) : (
              <Stack
                component={motion.div}
                variants={listVariants}
                initial="hidden"
                animate="show"
                divider={<Divider />}
                spacing={0}
              >
                <AnimatePresence>
                  {accounts.map((a) => {
                    const Icon = accountIcon(a.account_type);
                    const selected = transfer.from_account_id === a.id;
                    return (
                      <Box
                        key={a.id}
                        component={motion.div}
                        variants={rowVariants}
                        whileHover={{ x: 4 }}
                        onClick={() => handleUseAsFrom(a.id)}
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 2,
                          py: 1.75,
                          px: 1,
                          mx: -1,
                          borderRadius: 2,
                          cursor: "pointer",
                          bgcolor: selected ? "rgba(176,141,87,0.08)" : "transparent",
                          transition: "background-color 0.15s",
                        }}
                      >
                        <Box
                          sx={{
                            width: 42,
                            height: 42,
                            borderRadius: "10px",
                            bgcolor: "rgba(176,141,87,0.12)",
                            color: "secondary.dark",
                            display: "grid",
                            placeItems: "center",
                            flexShrink: 0,
                          }}
                        >
                          <Icon fontSize="small" />
                        </Box>
                        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                          <Typography sx={{ fontWeight: 600, textTransform: "capitalize" }}>
                            {a.account_type}
                          </Typography>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <Typography variant="body2" color="text.secondary">
                              {a.id} · Branch {a.branch_id}
                            </Typography>
                            <Tooltip title={copiedId === a.id ? "Copied!" : "Copy account ID"}>
                              <IconButton size="small" onClick={(e) => handleCopyId(e, a.id)} sx={{ p: 0.25 }}>
                                <ContentCopyOutlinedIcon sx={{ fontSize: 14 }} />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </Box>
                        <Box sx={{ textAlign: "right" }}>
                          <Typography sx={{ fontWeight: 700 }}>${a.balance.toFixed(2)}</Typography>
                          <Stack direction="row" spacing={0.5} justifyContent="flex-end" sx={{ mt: 0.25 }}>
                            <Tooltip title="Click to toggle active status">
                              <Chip
                                size="small"
                                label={statusUpdatingId === a.id ? "…" : a.active ? "Active" : "Inactive"}
                                color={a.active ? "success" : "default"}
                                onClick={(e) => handleToggleStatus(e, a)}
                                disabled={statusUpdatingId === a.id}
                                sx={{ cursor: "pointer" }}
                              />
                            </Tooltip>
                            <Tooltip title="Use as transfer recipient">
                              <Chip
                                size="small"
                                variant="outlined"
                                label="To"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setTransfer((prev) => ({ ...prev, to_account_id: a.id }));
                                }}
                                sx={{ cursor: "pointer" }}
                              />
                            </Tooltip>
                          </Stack>
                        </Box>
                      </Box>
                    );
                  })}
                </AnimatePresence>
                {accounts.length === 0 && (
                  <Typography color="text.secondary" sx={{ py: 3, textAlign: "center" }}>
                    No accounts found.
                  </Typography>
                )}
              </Stack>
            )}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 5 }}>
          <Paper
            component={motion.form}
            onSubmit={handleTransferSubmit}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            sx={{ p: 3 }}
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
                <SwapHorizOutlinedIcon fontSize="small" />
              </Box>
              <Typography variant="h6">Transfer Money</Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
              You can only transfer from an account you own.
            </Typography>

            {transferStatus.error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {transferStatus.error}
              </Alert>
            )}
            {transferStatus.success && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {transferStatus.success}
              </Alert>
            )}

            <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
              From Account ID
            </Typography>
            <TextField
              fullWidth
              required
              margin="none"
              sx={{ mb: 2 }}
              value={transfer.from_account_id}
              onChange={(e) => setTransfer({ ...transfer, from_account_id: e.target.value })}
            />
            <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
              To Account ID
            </Typography>
            <TextField
              fullWidth
              required
              sx={{ mb: 2 }}
              value={transfer.to_account_id}
              onChange={(e) => setTransfer({ ...transfer, to_account_id: e.target.value })}
            />
            <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
              Amount
            </Typography>
            <TextField
              type="number"
              fullWidth
              required
              slotProps={{ htmlInput: { step: "0.01", min: "0.01" } }}
              value={transfer.amount}
              onChange={(e) => setTransfer({ ...transfer, amount: e.target.value })}
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
              {submitting ? "Processing…" : "Transfer Funds"}
            </Button>
          </Paper>

          <RequestTransactionCard />

          {customer && <OpenAccountCard ownerId={customer.id} onCreated={loadData} />}
        </Grid>
      </Grid>
    </AppShell>
  );
}
