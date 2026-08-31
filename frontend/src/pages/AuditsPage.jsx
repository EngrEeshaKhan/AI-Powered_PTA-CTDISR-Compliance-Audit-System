import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Alert, Box, Card, CardContent, IconButton, Stack, TextField, Tooltip, Typography } from "@mui/material";
import { Search, VisibilityOutlined } from "@mui/icons-material";
import PageHeader from "../components/PageHeader";
import StatusChip from "../components/StatusChip";
import { getSavedAudits } from "../services/audits.service";
import { getApiError } from "../services/api";

function pick(item, keys, fallback = "—") {
  for (const k of keys) if (item?.[k] !== undefined && item?.[k] !== null) return item[k];
  return fallback;
}

export default function AuditsPage() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getSavedAudits().then(setItems).catch((e) => setError(getApiError(e, "Unable to load saved audits.")));
  }, []);

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    return !q ? items : items.filter((x) => JSON.stringify(x).toLowerCase().includes(q));
  }, [items, search]);

  return (
    <>
      <PageHeader eyebrow="AUDIT MANAGEMENT" title="Saved Audits" subtitle={`${items.length} persisted audit result(s).`} />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ p: 2 }}>
            <TextField fullWidth placeholder="Search audit ID, control, recommendation, status…" value={search} onChange={(e) => setSearch(e.target.value)} InputProps={{ startAdornment: <Search sx={{ mr: 1, color: "text.secondary" }} /> }} />
          </Box>
          <Box sx={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 820 }}>
              <thead><tr>{["Audit ID","Control","PTA Response","Recommendation","Action By","Status","Actions"].map(h => <th key={h} style={{ textAlign:"left", padding:"12px 16px", borderTop:"1px solid rgba(255,255,255,.06)", borderBottom:"1px solid rgba(255,255,255,.06)", color:"#71847b", fontSize:11 }}>{h}</th>)}</tr></thead>
              <tbody>
                {filtered.map((x, i) => {
                  const id = pick(x, ["audit_id","result_id","id"], String(i));
                  return (
                    <tr key={`${id}-${i}`}>
                      <td style={{ padding:"14px 16px", fontWeight:750 }}>{id}</td>
                      <td style={{ padding:"14px 16px" }}>{pick(x, ["control_id","control"])}</td>
                      <td style={{ padding:"14px 16px", maxWidth:280 }}>{pick(x, ["pta_response","response"])}</td>
                      <td style={{ padding:"14px 16px", maxWidth:300, color:"#9aaba3" }}>{pick(x, ["pta_recommendations","recommendation"])}</td>
                      <td style={{ padding:"14px 16px" }}>{pick(x, ["action_by"])}</td>
                      <td style={{ padding:"14px 16px" }}><StatusChip status={pick(x, ["status"], "")} /></td>
                      <td style={{ padding:"14px 16px" }}><Tooltip title="View audit"><IconButton component={Link} to={`/audits/${encodeURIComponent(id)}`}><VisibilityOutlined fontSize="small" /></IconButton></Tooltip></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {!filtered.length && <Box sx={{ p: 6, textAlign:"center" }}><Typography color="text.secondary">No saved audits found.</Typography></Box>}
          </Box>
        </CardContent>
      </Card>
    </>
  );
}