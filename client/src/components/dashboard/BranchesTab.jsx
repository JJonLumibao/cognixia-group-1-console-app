import { useEffect, useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Grid,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  CircularProgress,
} from "@mui/material";
import { getBranches, createBranch, updateBranchManager } from "../../api/branchManagers";

const emptyForm = { branch_code: "", branch_name: "", location: "", manager_id: "", staff_list: "" };

export default function BranchesTab() {
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [status, setStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);
  const [managerEdits, setManagerEdits] = useState({});

  const loadBranches = () => {
    setLoading(true);
    getBranches()
      .then(setBranches)
      .catch((err) => setLoadError(err.response?.data?.detail || "Failed to load branches."))
      .finally(() => setLoading(false));
  };

  useEffect(loadBranches, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setStatus({ error: "", success: "" });
    setSubmitting(true);
    try {
      await createBranch(form);
      setStatus({ error: "", success: "Branch created." });
      setForm(emptyForm);
      loadBranches();
    } catch (err) {
      setStatus({ error: err.response?.data?.detail || "Failed to create branch.", success: "" });
    } finally {
      setSubmitting(false);
    }
  };

  const handleAssignManager = async (branchCode) => {
    const managerId = managerEdits[branchCode];
    if (!managerId) return;
    try {
      await updateBranchManager(branchCode, managerId);
      loadBranches();
    } catch (err) {
      setStatus({ error: err.response?.data?.detail || "Failed to assign manager.", success: "" });
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 8 }}>
        <Paper sx={{ p: 2 }}>
          {loadError && <Alert severity="error" sx={{ mb: 2 }}>{loadError}</Alert>}
          {loading ? (
            <CircularProgress size={24} />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Code</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Manager ID</TableCell>
                  <TableCell>Reassign Manager</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {branches.map((b) => (
                  <TableRow key={b.branch_code}>
                    <TableCell>{b.branch_code}</TableCell>
                    <TableCell>{b.branch_name}</TableCell>
                    <TableCell>{b.location}</TableCell>
                    <TableCell>{b.manager_id}</TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", gap: 1 }}>
                        <TextField
                          size="small"
                          placeholder="User ID"
                          value={managerEdits[b.branch_code] || ""}
                          onChange={(e) =>
                            setManagerEdits({ ...managerEdits, [b.branch_code]: e.target.value })
                          }
                        />
                        <Button size="small" variant="outlined" onClick={() => handleAssignManager(b.branch_code)}>
                          Assign
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
                {branches.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      No branches yet.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </Paper>
      </Grid>

      <Grid size={{ xs: 12, md: 4 }}>
        <Paper sx={{ p: 3 }} component="form" onSubmit={handleCreate}>
          <Typography variant="h6" gutterBottom>
            Create Branch
          </Typography>

          {status.error && <Alert severity="error" sx={{ mb: 2 }}>{status.error}</Alert>}
          {status.success && <Alert severity="success" sx={{ mb: 2 }}>{status.success}</Alert>}

          <TextField
            label="Branch Code"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.branch_code}
            onChange={(e) => setForm({ ...form, branch_code: e.target.value })}
          />
          <TextField
            label="Branch Name"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.branch_name}
            onChange={(e) => setForm({ ...form, branch_name: e.target.value })}
          />
          <TextField
            label="Location"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
          />
          <TextField
            label="Manager User ID"
            fullWidth
            required
            margin="normal"
            size="small"
            helperText="Must belong to a user with the BRANCH_MANAGER role"
            value={form.manager_id}
            onChange={(e) => setForm({ ...form, manager_id: e.target.value })}
          />
          <TextField
            label="Staff List (comma-separated user IDs)"
            fullWidth
            margin="normal"
            size="small"
            value={form.staff_list}
            onChange={(e) => setForm({ ...form, staff_list: e.target.value })}
          />

          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={submitting}>
            {submitting ? "Creating..." : "Create Branch"}
          </Button>
        </Paper>
      </Grid>
    </Grid>
  );
}
