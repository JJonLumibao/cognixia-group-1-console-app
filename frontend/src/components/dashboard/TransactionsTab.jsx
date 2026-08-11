import { Box, Paper } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

const columns = [
  { field: "id", headerName: "Transaction ID", flex: 1 },
  { field: "type", headerName: "Type", flex: 0.7 },
  { field: "from_account_id", headerName: "From Account", flex: 1 },
  { field: "to_account_id", headerName: "To Account", flex: 1 },
  {
    field: "amount",
    headerName: "Amount",
    flex: 0.7,
    type: "number",
    valueFormatter: (value) => `$${Number(value).toFixed(2)}`,
  },
  {
    field: "timestamp",
    headerName: "Timestamp",
    flex: 1,
    valueFormatter: (value) => (value ? new Date(value).toLocaleString() : ""),
  },
];

export default function TransactionsTab({ transactions }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ height: 520 }}>
        <DataGrid rows={transactions} columns={columns} disableRowSelectionOnClick />
      </Box>
    </Paper>
  );
}
