import { useEffect, useState } from "react";
import { Box, Grid, Typography, Alert, CircularProgress, Chip } from "@mui/material";
import { motion } from "framer-motion";
import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlined";
import PaidOutlinedIcon from "@mui/icons-material/PaidOutlined";
import GroupsOutlinedIcon from "@mui/icons-material/GroupsOutlined";
import BadgeOutlinedIcon from "@mui/icons-material/BadgeOutlined";
import StatCard from "./StatCard";
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
    { label: "Total Accounts", value: performance.total_accounts, icon: AccountBalanceWalletOutlinedIcon },
    { label: "Active Accounts", value: performance.active_accounts, icon: CheckCircleOutlineIcon },
    {
      label: "Total Balance",
      value: performance.total_balance,
      decimals: 2,
      prefix: "$",
      icon: PaidOutlinedIcon,
      accent: true,
    },
    { label: "Total Staff", value: staff.total_staff, icon: GroupsOutlinedIcon },
    { label: "Total Tellers", value: staff.total_tellers, icon: BadgeOutlinedIcon },
  ];

  return (
    <Box>
      <Box
        component={motion.div}
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 2.5 }}
      >
        <Typography variant="h6">{performance.branch_name}</Typography>
        <Chip size="small" label={performance.branch_code} />
        <Typography variant="body2" color="text.secondary">
          {performance.location}
        </Typography>
      </Box>
      <Grid container spacing={2}>
        {cards.map((card, index) => (
          <Grid key={card.label} size={{ xs: 12, sm: 6, md: 2.4 }}>
            <StatCard {...card} index={index} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
