import api from "./api";

export async function getSavedAudits() {
  const { data } = await api.get("/audit-results");
  return data?.results || [];
}

export async function getSavedAudit(auditId) {
  const { data } = await api.get(`/audit-results/${encodeURIComponent(auditId)}`);
  return data?.result || data;
}

export async function updateSavedAudit(auditId, payload) {
  const { data } = await api.put(
    `/audit-results/${encodeURIComponent(auditId)}`,
    payload
  );
  return data?.result || data;
}

export async function deleteSavedAudit(auditId) {
  const { data } = await api.delete(
    `/audit-results/${encodeURIComponent(auditId)}`
  );
  return data;
}