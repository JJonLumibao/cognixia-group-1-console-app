import { useEffect, useState, useCallback } from "react";
import { Box, Tabs, Tab, Typography, Alert } from "@mui/material";
import { getAccounts } from "../api/accounts";
import { getCustomers } from "../api/customers";
import { getTransactions } from "../api/transactions";
import OverviewTab from "../components/dashboard/OverviewTab";
import AccountsTab from "../components/dashboard/AccountsTab";
import CustomersTab from "../components/dashboard/CustomersTab";
import TransactionsTab from "../components/dashboard/TransactionsTab";

export default function ManagerDashboardPage() {
  const [tab, setTab] = useState(0);
  const [accounts, setAccounts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [accountFilters, setAccountFilters] = useState({});
  const [error, setError] = useState("");

  const loadAccounts = useCallback(async (filters = accountFilters) => {
    try {
      const data = await getAccounts(filters);
      setAccounts(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load accounts.");
    }
  }, [accountFilters]);

  const loadCustomers = useCallback(async () => {
    try {
      setCustomers(await getCustomers());
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load customers.");
    }
  }, []);

  const loadTransactions = useCallback(async () => {
    try {
      setTransactions(await getTransactions());
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load transactions.");
    }
  }, []);

  useEffect(() => {
    loadAccounts({});
    loadCustomers();
    loadTransactions();
  }, []);

  const handleFiltersChange = (filters) => {
    setAccountFilters(filters);
    loadAccounts(filters);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Manager Dashboard
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Overview" />
        <Tab label="Accounts" />
        <Tab label="Customers" />
        <Tab label="Transactions" />
      </Tabs>

      {tab === 0 && <OverviewTab accounts={accounts} customers={customers} />}
      {tab === 1 && (
        <AccountsTab accounts={accounts} onFiltersChange={handleFiltersChange} onRefresh={() => loadAccounts()} />
      )}
      {tab === 2 && <CustomersTab customers={customers} onRefresh={loadCustomers} />}
      {tab === 3 && <TransactionsTab transactions={transactions} />}
    </Box>
  );
}
