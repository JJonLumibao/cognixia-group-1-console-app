import { useEffect, useMemo, useState, useCallback } from "react";
import { Box, Tabs, Tab, Typography, Alert } from "@mui/material";
import { getAccounts } from "../api/accounts";
import { getCustomers } from "../api/customers";
import { getTransactions } from "../api/transactions";
import { useAuth } from "../context/AuthContext";
import OverviewTab from "../components/dashboard/OverviewTab";
import AccountsTab from "../components/dashboard/AccountsTab";
import CustomersTab from "../components/dashboard/CustomersTab";
import TransactionsTab from "../components/dashboard/TransactionsTab";
import BranchPerformanceTab from "../components/dashboard/BranchPerformanceTab";
import BranchesTab from "../components/dashboard/BranchesTab";
import UsersTab from "../components/dashboard/UsersTab";

// Mirrors the role restrictions enforced server-side on each endpoint.
const TAB_DEFS = [
  { key: "branch", label: "Branch Performance", roles: ["BRANCH_MANAGER"] },
  { key: "overview", label: "Overview", roles: ["ADMIN"] },
  { key: "accounts", label: "Accounts", roles: ["ADMIN"] },
  { key: "customers", label: "Customers", roles: ["ADMIN", "BRANCH_MANAGER", "TELLER"] },
  { key: "transactions", label: "Transactions", roles: ["ADMIN", "TELLER"] },
  { key: "branches", label: "Branches", roles: ["ADMIN"] },
  { key: "users", label: "Users", roles: ["ADMIN"] },
];

export default function ManagerDashboardPage() {
  const { hasRole } = useAuth();
  const visibleTabs = useMemo(() => TAB_DEFS.filter((t) => hasRole(...t.roles)), [hasRole]);

  const [tab, setTab] = useState(0);
  const activeKey = visibleTabs[tab]?.key;

  const [accounts, setAccounts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [accountFilters, setAccountFilters] = useState({});
  const [error, setError] = useState("");

  const canSeeAccounts = hasRole("ADMIN");
  const canSeeCustomers = hasRole("ADMIN", "BRANCH_MANAGER", "TELLER");
  const canSeeTransactions = hasRole("ADMIN", "TELLER");

  const loadAccounts = useCallback(async (filters = accountFilters) => {
    try {
      setAccounts(await getAccounts(filters));
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
    if (canSeeAccounts) loadAccounts({});
    if (canSeeCustomers) loadCustomers();
    if (canSeeTransactions) loadTransactions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
        {visibleTabs.map((t) => (
          <Tab key={t.key} label={t.label} />
        ))}
      </Tabs>

      {activeKey === "branch" && <BranchPerformanceTab />}
      {activeKey === "overview" && <OverviewTab accounts={accounts} customers={customers} />}
      {activeKey === "accounts" && (
        <AccountsTab accounts={accounts} onFiltersChange={handleFiltersChange} onRefresh={() => loadAccounts()} />
      )}
      {activeKey === "customers" && <CustomersTab customers={customers} onRefresh={loadCustomers} />}
      {activeKey === "transactions" && (
        <TransactionsTab transactions={transactions} onRefresh={loadTransactions} />
      )}
      {activeKey === "branches" && <BranchesTab />}
      {activeKey === "users" && <UsersTab />}
    </Box>
  );
}
