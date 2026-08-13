import { useEffect, useMemo, useState, useCallback } from "react";
import { Box, ButtonBase, Alert } from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import { getAccounts } from "../api/accounts";
import { getCustomers } from "../api/customers";
import { getTransactions } from "../api/transactions";
import { useAuth } from "../context/AuthContext";
import AppShell from "../components/AppShell";
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

const ROLE_SUBTITLE = {
  ADMIN: "Full oversight across branches, accounts, and staff.",
  BRANCH_MANAGER: "Performance and staffing for your branch.",
  TELLER: "Customer service and day-to-day transactions.",
};

export default function ManagerDashboardPage() {
  const { hasRole, user } = useAuth();
  const visibleTabs = useMemo(() => TAB_DEFS.filter((t) => hasRole(...t.roles)), [hasRole]);

  const [activeKey, setActiveKey] = useState(() => visibleTabs[0]?.key);

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

  const primaryRole = user?.roles?.[0];

  return (
    <AppShell title="Dashboard" subtitle={ROLE_SUBTITLE[primaryRole] || "Manage your organization."}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box
        sx={{
          display: "inline-flex",
          bgcolor: "#EDEEF1",
          borderRadius: 2.5,
          p: 0.5,
          mb: 3,
          maxWidth: "100%",
          overflowX: "auto",
          gap: 0.25,
        }}
      >
        {visibleTabs.map((t) => {
          const active = activeKey === t.key;
          return (
            <ButtonBase
              key={t.key}
              onClick={() => setActiveKey(t.key)}
              disableRipple
              sx={{
                position: "relative",
                minHeight: 36,
                borderRadius: 2,
                px: 2,
                fontSize: 14,
                fontWeight: active ? 700 : 600,
                color: active ? "text.primary" : "text.secondary",
                whiteSpace: "nowrap",
                transition: "color 0.2s",
              }}
            >
              {active && (
                <Box
                  component={motion.div}
                  layoutId="dashboard-tab-pill"
                  transition={{ type: "spring", stiffness: 400, damping: 32 }}
                  sx={{
                    position: "absolute",
                    inset: 0,
                    borderRadius: 2,
                    bgcolor: "#fff",
                    boxShadow: "0 1px 3px rgba(20,27,45,0.12)",
                  }}
                />
              )}
              <Box component="span" sx={{ position: "relative" }}>
                {t.label}
              </Box>
            </ButtonBase>
          );
        })}
      </Box>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeKey}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
        >
          {activeKey === "branch" && <BranchPerformanceTab />}
          {activeKey === "overview" && <OverviewTab accounts={accounts} customers={customers} />}
          {activeKey === "accounts" && (
            <AccountsTab
              accounts={accounts}
              onFiltersChange={handleFiltersChange}
              onRefresh={() => loadAccounts()}
            />
          )}
          {activeKey === "customers" && <CustomersTab customers={customers} onRefresh={loadCustomers} />}
          {activeKey === "transactions" && (
            <TransactionsTab transactions={transactions} onRefresh={loadTransactions} />
          )}
          {activeKey === "branches" && <BranchesTab />}
          {activeKey === "users" && <UsersTab />}
        </motion.div>
      </AnimatePresence>
    </AppShell>
  );
}
