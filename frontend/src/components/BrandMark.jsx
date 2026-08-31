import { Box, Typography } from "@mui/material";

export default function BrandMark({ compact = false }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1.2 }}>
      <Box
        sx={{
          width: compact ? 34 : 42,
          height: compact ? 34 : 42,
          borderRadius: "11px",
          display: "grid",
          placeItems: "center",
          border: "1px solid rgba(34,197,94,.35)",
          background:
            "radial-gradient(circle, rgba(34,197,94,.25), rgba(34,197,94,.04) 65%)",
          color: "#55e88a",
          fontWeight: 800,
          letterSpacing: "-0.08em",
        }}
      >
        PTA
      </Box>
      {!compact && (
        <Box>
          <Typography fontWeight={750} lineHeight={1.05}>
            CTDISR Compliance
          </Typography>
          <Typography
            variant="caption"
            sx={{ color: "primary.main", fontWeight: 650 }}
          >
            Audit Intelligence
          </Typography>
        </Box>
      )}
    </Box>
  );
}