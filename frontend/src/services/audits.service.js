import api from "./api";

export async function getSavedAudits() {
  const { data } = await api.get("/audit-results");
  return data?.results || [];
}

export async function getSavedAudit(auditId) {
  const { data } = await api.get(
    `/audit-results/${encodeURIComponent(auditId)}`
  );
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

// =========================================================
// EXPORT ALL AUDIT REPORTS TO EXCEL
// =========================================================

export async function exportReportsToExcel() {
  const response = await api.get("/reports/export/excel", {
    responseType: "blob",
  });

  const blob = new Blob([response.data], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });

  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");

  link.href = url;
  link.download = "PTA_CTDSIR_Audit_Report.xlsx";

  document.body.appendChild(link);

  link.click();

  link.remove();

  window.URL.revokeObjectURL(url);
}