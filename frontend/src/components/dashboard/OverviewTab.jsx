import { useMemo } from "react";
import { Grid, Paper, Typography, Box } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

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
    { label: "Total Customers", value: customers.length },
    { label: "Active Customers", value: activeCustomers },
    { label: "Total Accounts", value: accounts.length },
    { label: "Active Accounts", value: activeAccounts },
    { label: "Total Balance", value: `$${totalBalance.toFixed(2)}` },
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
        {statCards.map((card) => (
          <Grid key={card.label} size={{ xs: 12, sm: 6, md: 2.4 }}>
            <Paper sx={{ p: 2, textAlign: "center" }}>
              <Typography variant="subtitle2" color="text.secondary">
                {card.label}
              </Typography>
              <Typography variant="h5">{card.value}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Branch Distribution & Performance
        </Typography>
        <Box sx={{ height: 360 }}>
          <DataGrid rows={branchStats} columns={columns} disableRowSelectionOnClick />
        </Box>
      </Paper>
    </Box>
  );
}
