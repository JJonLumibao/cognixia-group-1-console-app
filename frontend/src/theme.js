import { createTheme } from "@mui/material/styles";

// Jade brand palette — deep ink navy for authority/trust, a warm
// brass accent for a "premium bank" feel, calm neutrals for content.
const ink = {
  900: "#0B1220",
  800: "#111A2E",
  700: "#16213C",
  600: "#1C2A4A",
  500: "#243357",
};

const brass = {
  main: "#B08D57",
  light: "#D8BD8B",
  dark: "#8A6C3E",
};

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: ink[700],
      light: ink[500],
      dark: ink[900],
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: brass.main,
      light: brass.light,
      dark: brass.dark,
      contrastText: "#1A1300",
    },
    background: {
      default: "#F4F5F7",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#141B2D",
      secondary: "#5B6478",
    },
    divider: "#E4E7EC",
    success: { main: "#1E8E5A" },
    warning: { main: "#B7791F" },
    error: { main: "#C1403D" },
  },
  shape: {
    borderRadius: 10,
  },
  typography: {
    fontFamily: '"Inter", -apple-system, "Segoe UI", Roboto, sans-serif',
    h1: { fontFamily: '"Lora", serif' },
    h2: { fontFamily: '"Lora", serif' },
    h3: { fontFamily: '"Lora", serif', fontWeight: 600 },
    h4: { fontFamily: '"Lora", serif', fontWeight: 600, letterSpacing: -0.3 },
    h5: { fontWeight: 700, letterSpacing: -0.2 },
    h6: { fontWeight: 700 },
    subtitle1: { fontWeight: 600 },
    subtitle2: { fontWeight: 600, color: "#5B6478" },
    button: { fontWeight: 600, textTransform: "none" },
  },
  shadows: [
    "none",
    "0 1px 2px rgba(20,27,45,0.06)",
    "0 1px 3px rgba(20,27,45,0.08)",
    "0 2px 6px rgba(20,27,45,0.08)",
    "0 4px 10px rgba(20,27,45,0.08)",
    "0 4px 10px rgba(20,27,45,0.08)",
    "0 6px 16px rgba(20,27,45,0.10)",
    "0 6px 16px rgba(20,27,45,0.10)",
    "0 8px 20px rgba(20,27,45,0.10)",
    "0 8px 20px rgba(20,27,45,0.10)",
    "0 10px 24px rgba(20,27,45,0.12)",
    "0 10px 24px rgba(20,27,45,0.12)",
    "0 10px 24px rgba(20,27,45,0.12)",
    "0 12px 28px rgba(20,27,45,0.12)",
    "0 12px 28px rgba(20,27,45,0.12)",
    "0 12px 28px rgba(20,27,45,0.12)",
    "0 16px 32px rgba(20,27,45,0.14)",
    "0 16px 32px rgba(20,27,45,0.14)",
    "0 16px 32px rgba(20,27,45,0.14)",
    "0 20px 40px rgba(20,27,45,0.16)",
    "0 20px 40px rgba(20,27,45,0.16)",
    "0 20px 40px rgba(20,27,45,0.16)",
    "0 20px 40px rgba(20,27,45,0.16)",
    "0 20px 40px rgba(20,27,45,0.16)",
    "0 20px 40px rgba(20,27,45,0.16)",
    "0 24px 48px rgba(20,27,45,0.18)",
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { backgroundColor: "#F4F5F7" },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
        elevation1: {
          boxShadow: "0 1px 2px rgba(20,27,45,0.06), 0 1px 1px rgba(20,27,45,0.04)",
          border: "1px solid #E4E7EC",
        },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: {
          borderRadius: 8,
          paddingTop: 9,
          paddingBottom: 9,
          paddingLeft: 18,
          paddingRight: 18,
        },
        containedPrimary: {
          "&:hover": { backgroundColor: ink[900] },
        },
      },
    },
    MuiTextField: {
      defaultProps: { size: "small" },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          backgroundColor: "#FFFFFF",
        },
        notchedOutline: {
          borderColor: "#D9DCE3",
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 600, borderRadius: 6 },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 700,
          fontSize: 12,
          textTransform: "uppercase",
          letterSpacing: 0.4,
          color: "#5B6478",
          backgroundColor: "#FAFAFB",
          borderBottom: "1px solid #E4E7EC",
        },
        root: {
          borderBottom: "1px solid #EEF0F3",
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          "&:last-of-type td": { borderBottom: "none" },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          height: 3,
          borderRadius: 3,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 600,
          minHeight: 44,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: { borderRadius: 8 },
      },
    },
  },
});

export default theme;
