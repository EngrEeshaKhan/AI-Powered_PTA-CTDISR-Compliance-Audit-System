import { Chip } from "@mui/material";

const map = {
  compliant: { color: "success", label: "Compliant" },
  active: { color: "success", label: "Active" },
  finalized: { color: "success", label: "Finalized" },
  processed: { color: "success", label: "Processed" },
  generated: { color: "info", label: "Generated" },
  reviewed: { color: "info", label: "Reviewed" },
  partial: { color: "warning", label: "Partially Compliant" },
  draft: { color: "warning", label: "Draft" },
  processing: { color: "warning", label: "Processing" },
  non_compliant: { color: "error", label: "Non-Compliant" },
  "non-compliant": { color: "error", label: "Non-Compliant" },
  failed: { color: "error", label: "Failed" },
  inactive: { color: "default", label: "Inactive" },
};

export default function StatusChip({ status }) {
  const key = String(status || "").trim().toLowerCase().replaceAll(" ", "_");
  const config = map[key] || { color: "default", label: status || "Unknown" };
  return (
    <Chip
      size="small"
      label={config.label}
      color={config.color}
      variant="outlined"
      sx={{ fontWeight: 650, borderRadius: "7px" }}
    />
  );
}