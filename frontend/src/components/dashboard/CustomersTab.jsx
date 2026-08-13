import { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import BlockIcon from "@mui/icons-material/Block";
import ContentCopyOutlinedIcon from "@mui/icons-material/ContentCopyOutlined";
import { DataGrid } from "@mui/x-data-grid";
import { createCustomer, updateCustomer, deactivateCustomer } from "../../api/customers";

const emptyForm = { first_name: "", last_name: "", email: "", branch_id: "" };

export default function CustomersTab({ customers, onRefresh }) {
  const [form, setForm] = useState(emptyForm);
  const [status, setStatus] = useState({ error: "", success: "" });
  const [submitting, setSubmitting] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [editForm, setEditForm] = useState(emptyForm);
  const [editError, setEditError] = useState("");
  const [copiedId, setCopiedId] = useState("");

  const handleCopyId = async (id) => {
    try {
      await navigator.clipboard.writeText(id);
      setCopiedId(id);
      setTimeout(() => setCopiedId(""), 1500);
    } catch {
      // Clipboard access denied — nothing to do.
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setStatus({ error: "", success: "" });
    setSubmitting(true);
    try {
      await createCustomer(form);
      setStatus({ error: "", success: "Customer created." });
      setForm(emptyForm);
      onRefresh();
    } catch (err) {
      setStatus({ error: err.response?.data?.detail || "Failed to create customer.", success: "" });
    } finally {
      setSubmitting(false);
    }
  };

  const openEdit = (customer) => {
    setEditTarget(customer);
    setEditForm({
      first_name: customer.name?.split(" ")[0] || "",
      last_name: customer.name?.split(" ").slice(1).join(" ") || "",
      email: customer.email,
      branch_id: customer.branch_id,
    });
    setEditError("");
  };

  const handleUpdate = async () => {
    setEditError("");
    try {
      await updateCustomer(editTarget.id, editForm);
      setEditTarget(null);
      onRefresh();
    } catch (err) {
      setEditError(err.response?.data?.detail || "Failed to update customer.");
    }
  };

  const handleDeactivate = async (customer) => {
    try {
      await deactivateCustomer(customer.id);
      onRefresh();
    } catch (err) {
      setStatus({ error: err.response?.data?.detail || "Failed to deactivate customer.", success: "" });
    }
  };

  const columns = [
    {
      field: "id",
      headerName: "ID",
      flex: 1,
      renderCell: (params) => (
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, height: "100%" }}>
          <Typography variant="body2" noWrap>
            {params.value}
          </Typography>
          <Tooltip title={copiedId === params.value ? "Copied!" : "Copy customer ID"}>
            <IconButton size="small" onClick={() => handleCopyId(params.value)} sx={{ p: 0.25 }}>
              <ContentCopyOutlinedIcon sx={{ fontSize: 14 }} />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
    { field: "name", headerName: "Name", flex: 1 },
    { field: "email", headerName: "Email", flex: 1.2 },
    { field: "branch_id", headerName: "Branch", flex: 0.8 },
    { field: "active", headerName: "Active", flex: 0.5, valueFormatter: (value) => (value ? "Yes" : "No") },
    {
      field: "actions",
      headerName: "Actions",
      flex: 0.8,
      sortable: false,
      filterable: false,
      renderCell: (params) => (
        <Box>
          <IconButton size="small" onClick={() => openEdit(params.row)} title="Edit">
            <EditIcon fontSize="small" />
          </IconButton>
          <IconButton size="small" onClick={() => handleDeactivate(params.row)} title="Deactivate">
            <BlockIcon fontSize="small" />
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 8 }}>
        <Paper sx={{ p: 2 }}>
          <Box sx={{ height: 480 }}>
            <DataGrid rows={customers} columns={columns} disableRowSelectionOnClick />
          </Box>
        </Paper>
      </Grid>

      <Grid size={{ xs: 12, md: 4 }}>
        <Paper sx={{ p: 3 }} component="form" onSubmit={handleCreate}>
          <Typography variant="h6" gutterBottom>
            Add Customer
          </Typography>

          {status.error && <Alert severity="error" sx={{ mb: 2 }}>{status.error}</Alert>}
          {status.success && <Alert severity="success" sx={{ mb: 2 }}>{status.success}</Alert>}

          <TextField
            label="First Name"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.first_name}
            onChange={(e) => setForm({ ...form, first_name: e.target.value })}
          />
          <TextField
            label="Last Name"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.last_name}
            onChange={(e) => setForm({ ...form, last_name: e.target.value })}
          />
          <TextField
            label="Email"
            type="email"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <TextField
            label="Branch ID"
            fullWidth
            required
            margin="normal"
            size="small"
            value={form.branch_id}
            onChange={(e) => setForm({ ...form, branch_id: e.target.value })}
          />

          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={submitting}>
            {submitting ? "Creating..." : "Add Customer"}
          </Button>
        </Paper>
      </Grid>

      <Dialog open={!!editTarget} onClose={() => setEditTarget(null)} fullWidth maxWidth="xs">
        <DialogTitle>Edit Customer</DialogTitle>
        <DialogContent>
          {editError && <Alert severity="error" sx={{ mb: 2 }}>{editError}</Alert>}
          <TextField
            label="First Name"
            fullWidth
            margin="normal"
            size="small"
            value={editForm.first_name}
            onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
          />
          <TextField
            label="Last Name"
            fullWidth
            margin="normal"
            size="small"
            value={editForm.last_name}
            onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
          />
          <TextField
            label="Email"
            fullWidth
            margin="normal"
            size="small"
            value={editForm.email}
            onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
          />
          <TextField
            label="Branch ID"
            fullWidth
            margin="normal"
            size="small"
            value={editForm.branch_id}
            onChange={(e) => setEditForm({ ...editForm, branch_id: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditTarget(null)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpdate}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
}
