import { useState } from "react";
import { Alert, Box, Button, Card, CardContent, Checkbox, FormControlLabel, IconButton, InputAdornment, TextField, Typography } from "@mui/material";
import { ArrowForward, Visibility, VisibilityOff, ShieldOutlined } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getApiError } from "../services/api";
import BrandMark from "../components/BrandMark";

export default function LoginPage() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [show, setShow] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await signIn(form.username.trim(), form.password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(getApiError(err, "Unable to sign in."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Box sx={{ minHeight: "100vh", display: "grid", gridTemplateColumns: { md: "1.05fr .95fr" } }}>
      <Box
        sx={{
          display: { xs: "none", md: "flex" },
          p: 7,
          alignItems: "center",
          position: "relative",
          overflow: "hidden",
          background:
            "radial-gradient(circle at 25% 30%, rgba(34,197,94,.13), transparent 35%), linear-gradient(145deg,#080e0b,#050807)",
        }}
      >
        <Box sx={{ maxWidth: 650, position: "relative", zIndex: 1 }}>
          <BrandMark />
          <Typography variant="h2" sx={{ mt: 8, fontWeight: 800, maxWidth: 620 }}>
            Compliance intelligence for
            <Box component="span" sx={{ color: "primary.main" }}> CTDISR audits.</Box>
          </Typography>
          <Typography sx={{ mt: 2.2, maxWidth: 560, fontSize: 17, lineHeight: 1.75, color: "text.secondary" }}>
            A controlled workspace for knowledge-base management, CTDISR controls,
            evidence retrieval, AI-assisted assessment and audit reporting.
          </Typography>
          <Box sx={{ display: "flex", gap: 2, mt: 5 }}>
            {["RAG Evidence", "AI Assessment", "Audit Traceability"].map((x) => (
              <Box key={x} sx={{ px: 1.7, py: 1, border: "1px solid rgba(34,197,94,.18)", borderRadius: 2, color: "text.secondary", fontSize: 13 }}>
                {x}
              </Box>
            ))}
          </Box>
        </Box>
        <Box sx={{ position: "absolute", right: -130, bottom: -170, width: 470, height: 470, borderRadius: "50%", border: "1px solid rgba(34,197,94,.11)" }} />
        <Box sx={{ position: "absolute", right: 50, bottom: 40, width: 260, height: 260, borderRadius: "50%", border: "1px solid rgba(20,184,166,.10)" }} />
      </Box>

      <Box sx={{ display: "grid", placeItems: "center", p: { xs: 2, md: 5 }, background: "#080d0b" }}>
        <Card sx={{ width: "100%", maxWidth: 460 }}>
          <CardContent sx={{ p: { xs: 3, md: 4.2 } }}>
            <Box sx={{ display: { md: "none" }, mb: 4 }}><BrandMark /></Box>
            <Box sx={{ width: 46, height: 46, display: "grid", placeItems: "center", borderRadius: 2, color: "primary.main", background: "rgba(34,197,94,.09)", mb: 2.3 }}>
              <ShieldOutlined />
            </Box>
            <Typography variant="h4">Sign in</Typography>
            <Typography color="text.secondary" sx={{ mt: .7, mb: 3.3 }}>
              Access the PTA CTDISR compliance workspace.
            </Typography>
            {error && <Alert severity="error" sx={{ mb: 2.2 }}>{error}</Alert>}
            <Box component="form" onSubmit={submit}>
              <TextField
                fullWidth label="Username" autoComplete="username" required
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth label="Password" required
                type={show ? "text" : "password"} autoComplete="current-password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShow((v) => !v)} edge="end">
                        {show ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <FormControlLabel
                control={<Checkbox checked={remember} onChange={(e) => setRemember(e.target.checked)} />}
                label={<Typography variant="body2">Keep me signed in</Typography>}
                sx={{ my: 1 }}
              />
              <Button
                type="submit" fullWidth variant="contained" size="large"
                disabled={busy}
                endIcon={<ArrowForward />}
                sx={{ mt: 1, py: 1.25 }}
              >
                {busy ? "Authenticating…" : "Sign in"}
              </Button>
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 3, textAlign: "center" }}>
              Authorized users only • PTA CTDISR Compliance Audit System
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}