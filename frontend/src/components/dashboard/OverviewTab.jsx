import { useMemo } from "react";
import { Grid, Paper, Typography, Box } from "@mui/material";
import { motion } from "framer-motion";
import { DataGrid } from "@mui/x-data-grid";
import PeopleAltOutlinedIcon from "@mui/icons-material/PeopleAltOutlined";
import HowToRegOutlinedIcon from "@mui/icons-material/HowToRegOutlined";
import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlined";
import PaidOutlinedIcon from "@mui/icons-material/PaidOutlined";
import StatCard from "./StatCard";

export default function OverviewTab({ accounts, customers }) {
  const branchStats = useMemo(() => {
    const byBranch = new Map();
    for (const account of accounts) {
      const key = account.branch_id || "Unassigned";
      const current = byBranch.get(key) || { branchId: key, accountCount: 0, totalBalance: 0 };
      current.accountCount += 1;
      current.totalBalance += account.balance;
      byBranch.set(key, current);
    }
    return Array.from(byBranch.values()).map((row, idx) => ({ id: idx, ...row }));
  }, [accounts]);

  const totalBalance = accounts.reduce((sum, a) => sum + a.balance, 0);
  const activeAccounts = accounts.filter((a) => a.active).length;
  const activeCustomers = customers.filter((c) => c.active).length;

  const statCards = [
    { label: "Total Customers", value: customers.length, icon: PeopleAltOutlinedIcon },
    { label: "Active Customers", value: activeCustomers, icon: HowToRegOutlinedIcon },
    { label: "Total Accounts", value: accounts.length, icon: AccountBalanceWalletOutlinedIcon },
    { label: "Active Accounts", value: activeAccounts, icon: CheckCircleOutlineIcon },
    { label: "Total Balance", value: totalBalance, decimals: 2, prefix: "$", icon: PaidOutlinedIcon, accent: true },
  ];

  const columns = [
    { field: "branchId", headerName: "Branch", flex: 1 },
    { field: "accountCount", headerName: "Accounts", flex: 1, type: "number" },
    {
      field: "totalBalance",
      headerName: "Total Balance",
      flex: 1,
      type: "number",
      valueFormatter: (value) => `$${Number(value).toFixed(2)}`,
    },
  ];

  return (
    <Box>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {statCards.map((card, index) => (
          <Grid key={card.label} size={{ xs: 12, sm: 6, md: 2.4 }}>
            <StatCard {...card} index={index} />
          </Grid>
        ))}
      </Grid>

      <Paper
        component={motion.div}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
        sx={{ p: 2.5 }}
      >
        <Typography variant="h6" sx={{ mb: 2 }}>
          Branch Distribution &amp; Performance
        </Typography>
        <Box sx={{ height: 360 }}>
          <DataGrid rows={branchStats} columns={columns} disableRowSelectionOnClick />
        </Box>
      </Paper>
    </Box>
  );
}
