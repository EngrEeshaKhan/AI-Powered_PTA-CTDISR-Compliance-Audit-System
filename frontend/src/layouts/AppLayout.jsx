import { useState } from "react";
import {
  AppBar, Avatar, Box, Divider, Drawer, IconButton, List, ListItemButton,
  ListItemIcon, ListItemText, Menu, MenuItem, Stack, Toolbar, Tooltip, Typography,
} from "@mui/material";
import {
  AssessmentOutlined, DashboardOutlined, DescriptionOutlined, ExpandMore,
  Logout, Menu as MenuIcon, PeopleOutline, SecurityOutlined,
} from "@mui/icons-material";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import BrandMark from "../components/BrandMark";

const DRAWER = 246;

export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchor, setAnchor] = useState(null);
  const { user, isAdmin, signOut } = useAuth();
  const location = useLocation();

  const items = [
    { label: "Dashboard", path: "/dashboard", icon: <DashboardOutlined /> },
    { label: "Documents", path: "/documents", icon: <DescriptionOutlined /> },
    { label: "Controls", path: "/controls", icon: <SecurityOutlined /> },
    { label: "Audits", path: "/audits", icon: <AssessmentOutlined /> },
    ...(isAdmin ? [{ label: "Users", path: "/users", icon: <PeopleOutline /> }] : []),
  ];

  const drawer = (
    <Box className="sidebar-gradient" sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Box sx={{ p: 2.2, pb: 1.7 }}>
        <BrandMark />
      </Box>
      <Divider />
      <Box sx={{ px: 1.2, py: 1.7 }}>
        <Typography variant="overline" sx={{ px: 1.2, color: "text.secondary", fontWeight: 800 }}>
          Workspace
        </Typography>
        <List sx={{ mt: .5 }}>
          {items.map((item) => {
            const active = location.pathname === item.path || location.pathname.startsWith(`${item.path}/`);
            return (
              <ListItemButton
                key={item.path}
                component={NavLink}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                sx={{
                  borderRadius: 1.5,
                  mb: .35,
                  color: active ? "primary.main" : "text.secondary",
                  backgroundColor: active ? "rgba(34,197,94,.10)" : "transparent",
                  "&:hover": { backgroundColor: "rgba(255,255,255,.04)" },
                }}
              >
                <ListItemIcon sx={{ minWidth: 38, color: "inherit" }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: active ? 700 : 550 }} />
              </ListItemButton>
            );
          })}
        </List>
      </Box>
      <Box sx={{ mt: "auto", p: 1.6 }}>
        <Box
          sx={{
            p: 1.4, borderRadius: 2,
            border: "1px solid rgba(255,255,255,.07)",
            background: "rgba(255,255,255,.025)",
          }}
        >
          <Typography variant="caption" color="text.secondary">Signed in as</Typography>
          <Typography fontWeight={700} sx={{ mt: .2 }}>{user?.username}</Typography>
          <Typography variant="caption" sx={{ color: "primary.main" }}>
            {user?.role === "admin" ? "Administrator" : "Auditor"}
          </Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box className="app-shell">
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          ml: { md: `${DRAWER}px` },
          width: { md: `calc(100% - ${DRAWER}px)` },
          background: "rgba(7,11,10,.84)",
          backdropFilter: "blur(16px)",
          borderBottom: "1px solid rgba(255,255,255,.07)",
        }}
      >
        <Toolbar sx={{ minHeight: "64px !important" }}>
          <IconButton onClick={() => setMobileOpen(true)} sx={{ display: { md: "none" }, mr: 1 }}>
            <MenuIcon />
          </IconButton>
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" color="text.secondary">
              PTA / CTDISR / Compliance Operations
            </Typography>
          </Box>
          <Tooltip title="Account">
            <IconButton onClick={(e) => setAnchor(e.currentTarget)}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: "rgba(34,197,94,.18)", color: "primary.main", fontSize: 13 }}>
                {user?.username?.slice(0, 1)?.toUpperCase()}
              </Avatar>
              <ExpandMore sx={{ fontSize: 18, color: "text.secondary" }} />
            </IconButton>
          </Tooltip>
          <Menu anchorEl={anchor} open={Boolean(anchor)} onClose={() => setAnchor(null)}>
            <MenuItem onClick={() => { setAnchor(null); signOut(); }}>
              <ListItemIcon><Logout fontSize="small" /></ListItemIcon>
              Sign out
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          display: { xs: "none", md: "block" },
          "& .MuiDrawer-paper": { width: DRAWER, boxSizing: "border-box", borderRight: "1px solid rgba(255,255,255,.07)" },
        }}
        open
      >
        {drawer}
      </Drawer>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{ keepMounted: true }}
        sx={{ "& .MuiDrawer-paper": { width: DRAWER } }}
      >
        {drawer}
      </Drawer>

      <Box component="main" sx={{ ml: { md: `${DRAWER}px` }, pt: "64px", minHeight: "100vh" }}>
        <Box sx={{ p: { xs: 2, md: 3.2 }, maxWidth: 1800, mx: "auto" }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}