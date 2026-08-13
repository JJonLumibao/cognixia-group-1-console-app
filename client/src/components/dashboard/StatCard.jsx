import { Paper, Box, Typography } from "@mui/material";
import { motion } from "framer-motion";
import AnimatedNumber from "../AnimatedNumber";

export default function StatCard({ label, value, icon: Icon, accent = false, decimals = 0, prefix = "", index = 0 }) {
  return (
    <Paper
      component={motion.div}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.06, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -3, boxShadow: "0 10px 24px rgba(20,27,45,0.12)" }}
      sx={{ p: 2.25, height: "100%" }}
    >
      <Box sx={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <Box>
          <Typography variant="subtitle2" sx={{ color: "text.secondary", mb: 0.75 }}>
            {label}
          </Typography>
          <Typography sx={{ fontFamily: '"Lora", serif', fontWeight: 700, fontSize: 26, lineHeight: 1.1 }}>
            <AnimatedNumber value={value} prefix={prefix} format={(v) => v.toFixed(decimals)} />
          </Typography>
        </Box>
        {Icon && (
          <Box
            component={motion.div}
            initial={{ scale: 0, rotate: -8 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.4, delay: index * 0.06 + 0.15, type: "spring", stiffness: 260, damping: 18 }}
            sx={{
              width: 38,
              height: 38,
              borderRadius: "10px",
              display: "grid",
              placeItems: "center",
              flexShrink: 0,
              bgcolor: accent ? "rgba(176,141,87,0.12)" : "rgba(28,42,74,0.06)",
              color: accent ? "secondary.dark" : "primary.main",
            }}
          >
            <Icon fontSize="small" />
          </Box>
        )}
      </Box>
    </Paper>
  );
}
