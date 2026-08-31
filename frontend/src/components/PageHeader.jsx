import { Box, Button, Stack, Typography } from "@mui/material";

export default function PageHeader({ eyebrow, title, subtitle, action }) {
  return (
    <Box sx={{ mb: 3 }}>
      <Stack direction="row" justifyContent="space-between" gap={2} alignItems="flex-start">
        <Box>
          {eyebrow && (
            <Typography
              variant="overline"
              sx={{ color: "primary.main", fontWeight: 800, letterSpacing: ".12em" }}
            >
              {eyebrow}
            </Typography>
          )}
          <Typography variant="h4" sx={{ mt: eyebrow ? -0.4 : 0 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography color="text.secondary" sx={{ mt: 0.7 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        {action}
      </Stack>
    </Box>
  );
}