import { Box, Typography } from "@mui/material";
import { motion } from "framer-motion";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";

const panelVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
};

export default function AuthLayout({ eyebrow, title, subtitle, children }) {
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", bgcolor: "#F4F5F7" }}>
      <Box
        component={motion.div}
        variants={panelVariants}
        initial="hidden"
        animate="show"
        sx={{
          display: { xs: "none", md: "flex" },
          flexDirection: "column",
          justifyContent: "space-between",
          width: "42%",
          minWidth: 420,
          p: 6,
          background:
            "radial-gradient(circle at 15% 20%, rgba(176,141,87,0.25), transparent 45%), linear-gradient(160deg, #0B1220 0%, #16213C 60%, #1C2A4A 100%)",
          color: "#fff",
        }}
      >
        <Box component={motion.div} variants={itemVariants} sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          <Box
            component={motion.div}
            initial={{ scale: 0.5, rotate: -15, opacity: 0 }}
            animate={{ scale: 1, rotate: 0, opacity: 1 }}
            transition={{ duration: 0.6, type: "spring", stiffness: 240, damping: 16 }}
            sx={{
              width: 44,
              height: 44,
              borderRadius: "12px",
              display: "grid",
              placeItems: "center",
              background: "linear-gradient(135deg, #B08D57, #8A6C3E)",
            }}
          >
            <AccountBalanceIcon />
          </Box>
          <Box>
            <Typography sx={{ fontFamily: '"Lora", serif', fontWeight: 700, fontSize: 22, lineHeight: 1.1 }}>
              Jade
            </Typography>
            <Typography sx={{ fontSize: 11, color: "rgba(255,255,255,0.55)", letterSpacing: 1.5 }}>
              BANK &amp; TRUST
            </Typography>
          </Box>
        </Box>

        <Box component={motion.div} variants={itemVariants}>
          <Typography sx={{ fontFamily: '"Lora", serif', fontStyle: "italic", fontSize: 30, lineHeight: 1.35, mb: 2 }}>
            "Banking built on trust, precision, and a century of steady hands."
          </Typography>
          <Typography sx={{ color: "rgba(255,255,255,0.6)", fontSize: 14 }}>
            Secure account management for customers, tellers, branch managers, and administrators — all in one
            place.
          </Typography>
        </Box>

        <Typography
          component={motion.p}
          variants={itemVariants}
          sx={{ color: "rgba(255,255,255,0.4)", fontSize: 12, m: 0 }}
        >
          © {new Date().getFullYear()} Jade Bank &amp; Trust. Member FDIC.
        </Typography>
      </Box>

      <Box sx={{ flexGrow: 1, display: "flex", alignItems: "center", justifyContent: "center", p: 3 }}>
        <Box
          component={motion.div}
          variants={panelVariants}
          initial="hidden"
          animate="show"
          sx={{ width: "100%", maxWidth: 400 }}
        >
          <Box
            component={motion.div}
            variants={itemVariants}
            sx={{ display: { xs: "flex", md: "none" }, alignItems: "center", gap: 1.25, mb: 4 }}
          >
            <Box
              sx={{
                width: 36,
                height: 36,
                borderRadius: "10px",
                display: "grid",
                placeItems: "center",
                background: "linear-gradient(135deg, #B08D57, #8A6C3E)",
                color: "#fff",
              }}
            >
              <AccountBalanceIcon sx={{ fontSize: 20 }} />
            </Box>
            <Typography sx={{ fontFamily: '"Lora", serif', fontWeight: 700, fontSize: 19 }}>Jade</Typography>
          </Box>

          {eyebrow && (
            <Typography
              component={motion.p}
              variants={itemVariants}
              sx={{ fontSize: 12, fontWeight: 700, letterSpacing: 1, color: "secondary.dark", mb: 1, m: 0 }}
            >
              {eyebrow}
            </Typography>
          )}
          <Typography component={motion.h1} variants={itemVariants} variant="h4" sx={{ mb: 0.5, mt: 0.5 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography component={motion.p} variants={itemVariants} variant="body2" color="text.secondary" sx={{ mb: 4 }}>
              {subtitle}
            </Typography>
          )}

          <Box component={motion.div} variants={itemVariants}>
            {children}
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
