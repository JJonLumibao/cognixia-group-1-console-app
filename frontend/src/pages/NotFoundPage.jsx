import { Box, Typography, Button } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <Box sx={{ textAlign: "center", mt: 10 }}>
      <Typography variant="h3" gutterBottom>
        404
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        Page not found.
      </Typography>
      <Button variant="contained" component={RouterLink} to="/">
        Go Home
      </Button>
    </Box>
  );
}
