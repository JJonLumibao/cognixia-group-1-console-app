import { useEffect, useState } from "react";
import { Box, Grid, Paper, Typography, Alert, CircularProgress } from "@mui/material";
import { getBranchPerformance, getStaffMetrics } from "../../api/branchManagers";

export default function BranchPerformanceTab() {
  const [performance, setPerformance] = useState(null);
  const [staff, setStaff] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getBranchPerformance(), getStaffMetrics()])
      .then(([performanceData, staffData]) => {
        setPerformance(performanceData);
        setStaff(staffData);
      })
      .catch((err) => {
        setError(
          err.response?.status === 404
            ? "No branch is assigned to you yet. Ask an admin to set you as a branch's manager."
            : err.response?.data?.detail || "Failed to load branch performance."
        );
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress size={24} />;
  if (error) return <Alert severity="warning">{error}</Alert>;

  const cards = [
    { label: "Branch", value: `${performance.branch_name} (${performance.branch_code})` },
    { label: "Location", value: performance.location },
    { label: "Total Accounts", value: performance.total_accounts },
    { label: "Active Accounts", value: performance.active_accounts },
    { label: "Total Balance", value: `$${performance.total_balance.toFixed(2)}` },
    { label: "Total Staff", value: staff.total_staff },
    { label: "Total Tellers", value: staff.total_tellers },
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {performance.branch_name} Performance
      </Typography>
      <Grid container spacing={2}>
        {cards.map((card) => (
          <Grid key={card.label} size={{ xs: 12, sm: 6, md: 3 }}>
            <Paper sx={{ p: 2, textAlign: "center" }}>
              <Typography variant="subtitle2" color="text.secondary">
                {card.label}
              </Typography>
              <Typography variant="h6">{card.value}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
