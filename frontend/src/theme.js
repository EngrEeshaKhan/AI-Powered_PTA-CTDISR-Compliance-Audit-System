import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#22c55e", contrastText: "#041009" },
    secondary: { main: "#14b8a6" },
    background: {
      default: "#070b0a",
      paper: "#0d1412",
    },
    success: { main: "#22c55e" },
    warning: { main: "#eab308" },
    error: { main: "#ef4444" },
    info: { main: "#2dd4bf" },
    text: {
      primary: "#edf7f1",
      secondary: "#8da198",
    },
    divider: "rgba(255,255,255,0.08)",
  },
  typography: {
    fontFamily:
      '"Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    h4: { fontWeight: 700, letterSpacing: "-0.02em" },
    h5: { fontWeight: 700, letterSpacing: "-0.02em" },
    h6: { fontWeight: 650 },
    button: { textTransform: "none", fontWeight: 650 },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: "1px solid rgba(255,255,255,0.07)",
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: "linear-gradient(145deg, #101916 0%, #0b1210 100%)",
          border: "1px solid rgba(255,255,255,0.07)",
          boxShadow: "0 16px 40px rgba(0,0,0,0.22)",
        },
      },
    },
    MuiTextField: {
      defaultProps: { size: "small" },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderColor: "rgba(255,255,255,0.06)" },
        head: {
          color: "#71847b",
          fontWeight: 700,
          fontSize: 12,
          textTransform: "uppercase",
          letterSpacing: "0.06em",
        },
      },
    },
  },
});