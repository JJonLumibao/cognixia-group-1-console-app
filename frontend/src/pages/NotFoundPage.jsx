import { Box, Typography, Button } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";

export default function NotFoundPage() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "#F4F5F7",
        textAlign: "center",
        px: 3,
      }}
    >
      <Box
        sx={{
          width: 56,
          height: 56,
          borderRadius: "14px",
          display: "grid",
          placeItems: "center",
          background: "linear-gradient(135deg, #B08D57, #8A6C3E)",
          color: "#fff",
          mb: 3,
        }}
      >
        <AccountBalanceIcon />
      </Box>
      <Typography sx={{ fontFamily: '"Lora", serif', fontWeight: 700, fontSize: 56, lineHeight: 1, mb: 1 }}>
        404
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>
        We couldn't find the page you're looking for.
      </Typography>
      <Button variant="contained" size="large" component={RouterLink} to="/">
        Return Home
      </Button>
    </Box>
  );
}
