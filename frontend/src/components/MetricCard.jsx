import { Box, Card, CardContent, Stack, Typography } from "@mui/material";

export default function MetricCard({ label, value, caption, icon, tone = "primary" }) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent sx={{ p: 2.1 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={650}>
              {label}
            </Typography>
            <Typography
              className="metric-value"
              sx={{ fontSize: 27, fontWeight: 750, mt: 0.8 }}
            >
              {value ?? "—"}
            </Typography>
            {caption && (
              <Typography variant="caption" color="text.secondary">
                {caption}
              </Typography>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                width: 38,
                height: 38,
                borderRadius: 1.5,
                display: "grid",
                placeItems: "center",
                color: `${tone}.main`,
                backgroundColor: `${tone}.main`,
                opacity: 0.12,
                "& svg": { opacity: 8.3 },
              }}
            >
              {icon}
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}