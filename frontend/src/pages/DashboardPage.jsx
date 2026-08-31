import { useEffect, useMemo, useState } from "react";
import { Alert, Box, Card, CardContent, CircularProgress, Divider, Grid, Stack, Typography } from "@mui/material";
import { AssessmentOutlined, DescriptionOutlined, SecurityOutlined, PeopleOutline } from "@mui/icons-material";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as ChartTooltip } from "recharts";
import PageHeader from "../components/PageHeader";
import MetricCard from "../components/MetricCard";
import StatusChip from "../components/StatusChip";
import { getDashboardStatistics } from "../services/dashboard.service";
import { getApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const { isAdmin } = useAuth();

  useEffect(() => {
    getDashboardStatistics().then(setData).catch((e) => setError(getApiError(e, "Unable to load dashboard.")));
  }, []);

  const controls = data?.controls || {};
  const docs = data?.documents || {};
  const audits = data?.audits || {};

  const auditTotal = audits.total || 0;
  const auditData = [
    { name: "Draft", value: audits.draft || 0 },
    { name: "Generated", value: audits.generated || 0 },
    { name: "Reviewed", value: audits.reviewed || 0 },
    { name: "Finalized", value: audits.finalized || 0 },
  ].filter((x) => x.value > 0);

  return (
    <>
      <PageHeader
        eyebrow="OVERVIEW"
        title="Dashboard"
        subtitle="Live operational view of the CTDISR compliance platform."
      />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {!data && !error ? (
        <Box sx={{ minHeight: 420, display: "grid", placeItems: "center" }}><CircularProgress /></Box>
      ) : (
        <Stack spacing={2.2}>
          <Grid container spacing={1.7}>
            <Grid item xs={12} sm={6} lg={3}>
              <MetricCard label="Total Controls" value={controls.total} caption={`${controls.active || 0} active`} icon={<SecurityOutlined />} />
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>
              <MetricCard label="Knowledge Documents" value={docs.total} caption={`${docs.policies || 0} policies · ${docs.advisories || 0} advisories`} icon={<DescriptionOutlined />} tone="secondary" />
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>
              <MetricCard label="Saved Audits" value={audits.total} caption={`${audits.finalized || 0} finalized`} icon={<AssessmentOutlined />} tone="success" />
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>
              <MetricCard label="CTDISR Coverage" value={controls.total ? "Active" : "—"} caption="Control registry status" icon={<PeopleOutline />} tone="info" />
            </Grid>
          </Grid>

          <Grid container spacing={2}>
            <Grid item xs={12} lg={7}>
              <Card sx={{ height: "100%" }}>
                <CardContent sx={{ p: 2.4 }}>
                  <Typography fontWeight={750}>Knowledge base</Typography>
                  <Typography variant="body2" color="text.secondary">Documents currently visible to the backend dashboard.</Typography>
                  <Grid container spacing={1.3} sx={{ mt: 1.5 }}>
                    {[
                      ["Policies", docs.policies],
                      ["Advisories", docs.advisories],
                      ["CTDISR", docs.ctdisr],
                      ["Assets", docs.assets],
                    ].map(([label, value]) => (
                      <Grid item xs={6} sm={3} key={label}>
                        <Box sx={{ p: 1.7, borderRadius: 2, border: "1px solid rgba(255,255,255,.06)", background: "rgba(255,255,255,.02)" }}>
                          <Typography variant="caption" color="text.secondary">{label}</Typography>
                          <Typography sx={{ fontSize: 24, fontWeight: 750, mt: .4 }}>{value ?? 0}</Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                  <Divider sx={{ my: 2 }} />
                  <Stack direction="row" spacing={2} flexWrap="wrap">
                    <Stack direction="row" spacing={1} alignItems="center"><Box className="status-dot" sx={{ bgcolor: "success.main" }} />Stored source files</Stack>
                    <Stack direction="row" spacing={1} alignItems="center"><Box className="status-dot" sx={{ bgcolor: "secondary.main" }} />Indexed knowledge</Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} lg={5}>
              <Card sx={{ height: "100%" }}>
                <CardContent sx={{ p: 2.4 }}>
                  <Typography fontWeight={750}>Audit lifecycle</Typography>
                  <Typography variant="body2" color="text.secondary">Saved audit results by workflow state.</Typography>
                  <Box sx={{ height: 220, position: "relative", mt: 1 }}>
                    {auditData.length ? (
                      <>
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie data={auditData} dataKey="value" nameKey="name" innerRadius={62} outerRadius={82} paddingAngle={3}>
                              {auditData.map((_, i) => <Cell key={i} fill={["#22c55e", "#2dd4bf", "#eab308", "#14b8a6"][i % 4]} />)}
                            </Pie>
                            <ChartTooltip />
                          </PieChart>
                        </ResponsiveContainer>
                        <Box sx={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", pointerEvents: "none" }}>
                          <Box sx={{ textAlign: "center" }}>
                            <Typography sx={{ fontSize: 27, fontWeight: 800 }}>{auditTotal}</Typography>
                            <Typography variant="caption" color="text.secondary">audits</Typography>
                          </Box>
                        </Box>
                      </>
                    ) : (
                      <Box sx={{ height: "100%", display: "grid", placeItems: "center" }}>
                        <Typography color="text.secondary">No saved audit results yet.</Typography>
                      </Box>
                    )}
                  </Box>
                  <Stack spacing={1}>
                    {[
                      ["Draft", audits.draft],
                      ["Generated", audits.generated],
                      ["Reviewed", audits.reviewed],
                      ["Finalized", audits.finalized],
                    ].map(([label, value]) => (
                      <Stack direction="row" justifyContent="space-between" key={label}>
                        <Typography variant="body2" color="text.secondary">{label}</Typography>
                        <Typography variant="body2" fontWeight={700}>{value || 0}</Typography>
                      </Stack>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Card>
            <CardContent sx={{ p: 2.4 }}>
              <Typography fontWeight={750}>Platform readiness</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Current backend capabilities surfaced in this frontend.</Typography>
              <Grid container spacing={1.4}>
                {[
                  ["Authentication", "JWT login + role", "active"],
                  ["CTDISR Controls", "List / detail / admin CRUD", "active"],
                  ["AI Audit", "Evidence + Llama pipeline", "active"],
                  ["Saved Results", "View / edit / delete", "active"],
                  ["Document Upload", "Upload + automatic processing", "active"],
                  ["Document Inventory", "List endpoint", "inactive"],
                ].map(([title, detail, status]) => (
                  <Grid item xs={12} sm={6} lg={4} key={title}>
                    <Box sx={{ p: 1.6, border: "1px solid rgba(255,255,255,.06)", borderRadius: 2 }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography fontWeight={650}>{title}</Typography>
                        <StatusChip status={status} />
                      </Stack>
                      <Typography variant="caption" color="text.secondary">{detail}</Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Stack>
      )}
    </>
  );
}