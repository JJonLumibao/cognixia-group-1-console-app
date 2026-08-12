import { useEffect, useState } from "react";
import { Box, Paper, Alert, CircularProgress } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { getUsers } from "../../api/users";

const columns = [
  { field: "id", headerName: "User ID", flex: 1 },
  { field: "email", headerName: "Email", flex: 1.5 },
  { field: "role", headerName: "Role", flex: 1 },
  { field: "active", headerName: "Active", flex: 0.6, valueFormatter: (value) => (value ? "Yes" : "No") },
];

export default function UsersTab() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUsers()
      .then(setUsers)
      .catch((err) => setError(err.response?.data?.detail || "Failed to load users."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress size={24} />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ height: 480 }}>
        <DataGrid rows={users} columns={columns} disableRowSelectionOnClick />
      </Box>
    </Paper>
  );
}
