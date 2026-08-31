import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Alert, Box, Button, Card, CardContent, CircularProgress, Divider, Grid, Stack, TextField, Typography } from "@mui/material";
import { ArrowBack, PlayArrow, SaveOutlined } from "@mui/icons-material";
import PageHeader from "../components/PageHeader";
import StatusChip from "../components/StatusChip";
import { getControl, runAudit, updateControl } from "../services/controls.service";
import { getApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function ControlDetailsPage() {
  const { controlId } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const id = decodeURIComponent(controlId);
  const [control, setControl] = useState(null);
  const [form, setForm] = useState(null);
  const [busy, setBusy] = useState(true);
  const [auditBusy, setAuditBusy] = useState(false);
  const [saveBusy, setSaveBusy] = useState(false);
  const [error, setError] = useState("");
  const [auditResult, setAuditResult] = useState(null);

  async function load() {
    setBusy(true); setError("");
    try {
      const data = await getControl(id);
      setControl(data); setForm(data);
    } catch (e) { setError(getApiError(e, "Unable to load control.")); }
    finally { setBusy(false); }
  }
  useEffect(() => { load(); }, [id]);

  async function audit() {
    setAuditBusy(true); setError(""); setAuditResult(null);
    try {
      const result = await runAudit(id, { top_k: 5, max_new_tokens: 400 });
      setAuditResult(result?.result || result);
    } catch (e) { setError(getApiError(e, "AI audit failed.")); }
    finally { setAuditBusy(false); }
  }

  async function save() {
    setSaveBusy(true); setError("");
    try {
      const updated = await updateControl(id, {
        control_level: form.control_level,
        control_description: form.control_description,
        interpretation: form.interpretation,
        pta_response: form.pta_response,
        pta_recommendations: form.pta_recommendations,
        action_by: form.action_by,
        ntc_comments: form.ntc_comments,
        source_document: form.source_document,
      });
      setControl(updated); setForm(updated);
    } catch (e) { setError(getApiError(e, "Unable to update control.")); }
    finally { setSaveBusy(false); }
  }

  if (busy) return <Box sx={{ minHeight: 400, display: "grid", placeItems: "center" }}><CircularProgress /></Box>;
  if (!control || !form) return <Alert severity="error">{error || "Control not found."}</Alert>;

  return (
    <>
      <Button startIcon={<ArrowBack />} onClick={() => navigate("/controls")} sx={{ mb: 1 }}>Back to controls</Button>
      <PageHeader
        eyebrow={`CONTROL ${id}`}
        title={control.control_description || id}
        subtitle={`Level ${control.control_level} · Source ${control.source_document || "Not specified"}`}
        action={
          <Stack direction="row" spacing={1}>
            {isAdmin && <Button variant="outlined" startIcon={<SaveOutlined />} onClick={save} disabled={saveBusy}>{saveBusy ? "Saving…" : "Save Changes"}</Button>}
            <Button variant="contained" startIcon={<PlayArrow />} onClick={audit} disabled={auditBusy}>{auditBusy ? "Running AI audit…" : "Audit Control"}</Button>
          </Stack>
        }
      />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Grid container spacing={2}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography fontWeight={750}>Control details</Typography>
                <StatusChip status={control.status} />
              </Stack>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={1.6}>
                {[
                  ["control_id", "Control ID", false],
                  ["control_level", "Control Level", true],
                  ["control_description", "Control Requirement", true],
                  ["interpretation", "Interpretation", true],
                  ["pta_response", "PTA Response", true],
                  ["pta_recommendations", "PTA Recommendations", true],
                  ["action_by", "Action By", true],
                  ["ntc_comments", "NTC Comments", true],
                ].map(([key, label, multiline]) => (
                  <Grid item xs={12} md={key === "control_id" || key === "control_level" ? 6 : 12} key={key}>
                    <TextField
                      fullWidth label={label} value={form[key] || ""} disabled={key === "control_id"}
                      multiline={multiline} minRows={multiline ? 3 : 1}
                      onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                    />
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card sx={{ height: "100%" }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography fontWeight={750}>AI audit output</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: .5, mb: 2 }}>
                Evidence retrieval → context building → fine-tuned Llama assessment.
              </Typography>
              {!auditResult ? (
                <Box sx={{ p: 3, borderRadius: 2, border: "1px dashed rgba(255,255,255,.10)", textAlign: "center" }}>
                  <PlayArrow sx={{ color: "primary.main", fontSize: 34 }} />
                  <Typography fontWeight={650} sx={{ mt: 1 }}>No run in this session</Typography>
                  <Typography variant="caption" color="text.secondary">Run the AI audit to populate findings and recommendations.</Typography>
                </Box>
              ) : (
                <Stack spacing={1.6}>
                  {Object.entries(auditResult).filter(([k]) => !["success","message"].includes(k)).map(([key, value]) => (
                    <Box key={key}>
                      <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: ".06em" }}>{key.replaceAll("_"," ")}</Typography>
                      <Typography sx={{ whiteSpace: "pre-wrap", mt: .3, lineHeight: 1.6 }}>
                        {typeof value === "object" ? JSON.stringify(value, null, 2) : String(value ?? "—")}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </>
  );
}