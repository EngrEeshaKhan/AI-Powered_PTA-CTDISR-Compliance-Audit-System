import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Alert, Button, Card, CardContent, Divider, Grid, Stack, TextField, Typography } from "@mui/material";
import { ArrowBack, SaveOutlined } from "@mui/icons-material";
import PageHeader from "../components/PageHeader";
import StatusChip from "../components/StatusChip";
import { getSavedAudit, updateSavedAudit } from "../services/audits.service";
import { getApiError } from "../services/api";

export default function AuditDetailsPage() {
  const { auditId } = useParams();
  const navigate = useNavigate();
  const id = decodeURIComponent(auditId);
  const [audit, setAudit] = useState(null);
  const [form, setForm] = useState({});
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getSavedAudit(id)
      .then((data) => { setAudit(data); setForm(data || {}); })
      .catch((e) => setError(getApiError(e, "Unable to load audit.")));
  }, [id]);

  async function save() {
    setSaving(true); setError("");
    try {
      const updated = await updateSavedAudit(id, {
        pta_response: form.pta_response,
        pta_recommendations: form.pta_recommendations,
        action_by: form.action_by,
        ntc_comments: form.ntc_comments,
      });
      setAudit(updated); setForm(updated || {});
    } catch (e) { setError(getApiError(e, "Unable to save audit.")); }
    finally { setSaving(false); }
  }

  if (error && !audit) return <Alert severity="error">{error}</Alert>;
  if (!audit) return <Typography color="text.secondary">Loading audit…</Typography>;

  return (
    <>
      <Button startIcon={<ArrowBack />} onClick={() => navigate("/audits")} sx={{ mb: 1 }}>Back to audits</Button>
      <PageHeader
        eyebrow={`AUDIT ${id}`}
        title={`Control ${audit.control_id || audit.control || "—"}`}
        subtitle="Review, edit and persist the generated PTA audit result."
        action={<Button variant="contained" startIcon={<SaveOutlined />} onClick={save} disabled={saving}>{saving ? "Saving…" : "Save Review"}</Button>}
      />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography fontWeight={750}>Audit assessment</Typography>
                <StatusChip status={audit.status} />
              </Stack>
              <Divider sx={{ my: 2 }} />
              <Stack spacing={2}>
                <TextField label="PTA Response" multiline minRows={4} fullWidth value={form.pta_response || ""} onChange={(e) => setForm({ ...form, pta_response: e.target.value })} />
                <TextField label="PTA Recommendations" multiline minRows={4} fullWidth value={form.pta_recommendations || ""} onChange={(e) => setForm({ ...form, pta_recommendations: e.target.value })} />
                <TextField label="Action By" fullWidth value={form.action_by || ""} onChange={(e) => setForm({ ...form, action_by: e.target.value })} />
                <TextField label="NTC Comments" multiline minRows={4} fullWidth value={form.ntc_comments || ""} onChange={(e) => setForm({ ...form, ntc_comments: e.target.value })} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Typography fontWeight={750}>Audit metadata</Typography>
              <Stack spacing={1.4} sx={{ mt: 2 }}>
                {Object.entries(audit).filter(([k]) => !["pta_response","pta_recommendations","action_by","ntc_comments"].includes(k)).slice(0, 14).map(([key, value]) => (
                  <Stack direction="row" justifyContent="space-between" gap={2} key={key}>
                    <Typography variant="caption" color="text.secondary">{key.replaceAll("_"," ")}</Typography>
                    <Typography variant="body2" textAlign="right">{typeof value === "object" ? JSON.stringify(value) : String(value ?? "—")}</Typography>
                  </Stack>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </>
  );
}