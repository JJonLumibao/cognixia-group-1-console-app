import { useState } from "react";
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  Chip,
  IconButton,
  Divider,
  Tooltip,
} from "@mui/material";
import { Link as RouterLink, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import SpaceDashboardOutlinedIcon from "@mui/icons-material/SpaceDashboardOutlined";
import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import LogoutOutlinedIcon from "@mui/icons-material/LogoutOutlined";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import { useAuth } from "../context/AuthContext";
import { STAFF_ROLES } from "../constants/roles";

const DRAWER_WIDTH = 264;

const ROLE_LABELS = {
  ADMIN: "Administrator",
  BRANCH_MANAGER: "Branch Manager",
  TELLER: "Teller",
  CUSTOMER: "Customer",
};

function initialsFor(email) {
  if (!email) return "?";
  return email.slice(0, 2).toUpperCase();
}

function SidebarContent({ onNavigate }) {
  const { user, hasRole, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = hasRole(...STAFF_ROLES)
    ? [{ label: "Dashboard", to: "/dashboard", icon: SpaceDashboardOutlinedIcon }]
    : [{ label: "My Accounts", to: "/portal", icon: AccountBalanceWalletOutlinedIcon }];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const primaryRole = user?.roles?.[0];

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.25, px: 3, py: 3 }}>
        <Box
          component={motion.div}
          initial={{ scale: 0.6, rotate: -12, opacity: 0 }}
          animate={{ scale: 1, rotate: 0, opacity: 1 }}
          transition={{ duration: 0.5, type: "spring", stiffness: 260, damping: 18 }}
          sx={{
            width: 36,
            height: 36,
            borderRadius: "10px",
            display: "grid",
            placeItems: "center",
            background: "linear-gradient(135deg, #B08D57, #8A6C3E)",
            color: "#fff",
            flexShrink: 0,
          }}
        >
          <AccountBalanceIcon sx={{ fontSize: 20 }} />
        </Box>
        <Box>
          <Typography
            sx={{ fontFamily: '"Lora", serif', fontWeight: 700, fontSize: 19, lineHeight: 1.1, color: "#fff" }}
          >
            Jade
          </Typography>
          <Typography sx={{ fontSize: 11, color: "rgba(255,255,255,0.55)", letterSpacing: 1 }}>
            BANK &amp; TRUST
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ borderColor: "rgba(255,255,255,0.08)" }} />

      <List sx={{ px: 2, py: 2, flexGrow: 1 }}>
        {navItems.map((item) => {
          const active = location.pathname.startsWith(item.to);
          const Icon = item.icon;
          return (
            <ListItemButton
              key={item.to}
              component={RouterLink}
              to={item.to}
              onClick={onNavigate}
              disableRipple
              sx={{
                position: "relative",
                borderRadius: 2,
                mb: 0.5,
                overflow: "hidden",
                color: active ? "#fff" : "rgba(255,255,255,0.65)",
                "&:hover": { backgroundColor: active ? undefined : "rgba(255,255,255,0.06)" },
              }}
            >
              {active && (
                <Box
                  component={motion.div}
                  layoutId="sidebar-active-pill"
                  transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  sx={{
                    position: "absolute",
                    inset: 0,
                    borderRadius: 2,
                    bgcolor: "rgba(176,141,87,0.18)",
                  }}
                />
              )}
              <ListItemIcon
                sx={{ minWidth: 36, position: "relative", color: active ? "#D8BD8B" : "rgba(255,255,255,0.5)" }}
              >
                <Icon fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                sx={{ position: "relative" }}
                slotProps={{ primary: { sx: { fontWeight: active ? 700 : 500, fontSize: 14 } } }}
              />
            </ListItemButton>
          );
        })}
      </List>

      <Box sx={{ p: 2 }}>
        <Divider sx={{ borderColor: "rgba(255,255,255,0.08)", mb: 2 }} />
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, px: 1, mb: 1.5 }}>
          <Avatar sx={{ width: 34, height: 34, bgcolor: "#B08D57", fontSize: 13, fontWeight: 700 }}>
            {initialsFor(user?.email)}
          </Avatar>
          <Box sx={{ minWidth: 0, flexGrow: 1 }}>
            <Typography noWrap sx={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>
              {user?.email}
            </Typography>
            {primaryRole && (
              <Chip
                label={ROLE_LABELS[primaryRole] || primaryRole}
                size="small"
                sx={{
                  height: 18,
                  fontSize: 10,
                  mt: 0.25,
                  bgcolor: "rgba(255,255,255,0.08)",
                  color: "rgba(255,255,255,0.75)",
                }}
              />
            )}
          </Box>
          <Tooltip title="Log out">
            <IconButton size="small" onClick={handleLogout} sx={{ color: "rgba(255,255,255,0.55)" }}>
              <LogoutOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
    </Box>
  );
}

export default function AppShell({ title, subtitle, actions, children }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <Box
        component="nav"
        sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              backgroundColor: "#111A2E",
              backgroundImage: "none",
            },
          }}
        >
          <Box sx={{ display: "flex", justifyContent: "flex-end", p: 1 }}>
            <IconButton onClick={() => setMobileOpen(false)} sx={{ color: "rgba(255,255,255,0.6)" }}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
          <SidebarContent onNavigate={() => setMobileOpen(false)} />
        </Drawer>

        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              boxSizing: "border-box",
              border: "none",
              backgroundColor: "#111A2E",
              backgroundImage: "none",
            },
          }}
          open
        >
          <SidebarContent />
        </Drawer>
      </Box>

      <Box sx={{ flexGrow: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        <Box
          sx={{
            display: { xs: "flex", md: "none" },
            alignItems: "center",
            gap: 1.5,
            px: 2,
            py: 1.5,
            bgcolor: "#111A2E",
          }}
        >
          <IconButton onClick={() => setMobileOpen(true)} sx={{ color: "#fff" }}>
            <MenuIcon />
          </IconButton>
          <Typography sx={{ color: "#fff", fontWeight: 700, fontFamily: '"Lora", serif' }}>Jade</Typography>
        </Box>

        {(title || actions) && (
          <Box
            component={motion.div}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            sx={{
              px: { xs: 3, md: 5 },
              pt: { xs: 3, md: 5 },
              pb: 2,
              display: "flex",
              alignItems: { xs: "flex-start", sm: "center" },
              justifyContent: "space-between",
              flexDirection: { xs: "column", sm: "row" },
              gap: 1.5,
            }}
          >
            <Box>
              {title && (
                <Typography variant="h4" sx={{ color: "text.primary" }}>
                  {title}
                </Typography>
              )}
              {subtitle && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {subtitle}
                </Typography>
              )}
            </Box>
            {actions && <Box>{actions}</Box>}
          </Box>
        )}

        <Box
          component={motion.div}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
          sx={{ px: { xs: 3, md: 5 }, pb: 5, flexGrow: 1 }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}
