import { useEffect, useState } from "react";
import { Alert, Button, Card, CardContent, Dialog, DialogActions, DialogContent, DialogTitle, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from "@mui/material";
import { Add } from "@mui/icons-material";
import PageHeader from "../components/PageHeader";
import { createUser, getUsers } from "../services/auth.service";
import { getApiError } from "../services/api";
import StatusChip from "../components/StatusChip";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ username: "", password: "", role: "auditor" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    try { setUsers(await getUsers()); } catch (e) { setError(getApiError(e, "Unable to load users.")); }
  }
  useEffect(() => { load(); }, []);

  async function save() {
    setBusy(true); setError("");
    try {
      await createUser(form);
      setOpen(false); setForm({ username: "", password: "", role: "auditor" }); await load();
    } catch (e) { setError(getApiError(e, "Unable to create user.")); }
    finally { setBusy(false); }
  }

  return (
    <>
      <PageHeader eyebrow="ADMINISTRATION" title="Users" subtitle="Administrator-only account management." action={<Button variant="contained" startIcon={<Add />} onClick={() => setOpen(true)}>Add Auditor</Button>} />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <Table>
            <TableHead><TableRow><TableCell>Username</TableCell><TableCell>Role</TableCell><TableCell>Status</TableCell></TableRow></TableHead>
            <TableBody>{users.map((u) => <TableRow key={u.username}><TableCell sx={{ fontWeight: 700 }}>{u.username}</TableCell><TableCell>{u.role}</TableCell><TableCell><StatusChip status={u.is_active === false ? "inactive" : "active"} /></TableCell></TableRow>)}</TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={open} onClose={() => !busy && setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Create auditor account</DialogTitle>
        <DialogContent>
          <Stack spacing={1.7} sx={{ mt: 1 }}>
            <TextField fullWidth label="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
            <TextField fullWidth type="password" label="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <Typography variant="caption" color="text.secondary">The current backend intentionally allows administrators to create auditor accounts only.</Typography>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={save} disabled={busy || !form.username || !form.password}>{busy ? "Creating…" : "Create Auditor"}</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}