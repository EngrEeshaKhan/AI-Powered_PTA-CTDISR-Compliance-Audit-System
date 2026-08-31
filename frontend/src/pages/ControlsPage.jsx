
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  MenuItem,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";

import {
  AddOutlined,
  BlockOutlined,
  EditOutlined,
  PlayArrowOutlined,
  RefreshOutlined,
  VisibilityOutlined,
} from "@mui/icons-material";

import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { useAuth } from "../context/AuthContext";

import {
  getControls,
  getControlStatistics,
  createControl,
  updateControl,
  deactivateControl,
  runAudit,
} from "../services/controls.service";

import { getApiError } from "../services/api";


const emptyForm = {
  control_id: "",
  control_level: "CL1",
  control_description: "",
  interpretation: "",
  pta_response: "",
  pta_recommendations: "",
  action_by: "",
  ntc_comments: "",
  source_document: "",
};


export default function ControlsPage() {
  const { isAdmin } = useAuth();

  const [controls, setControls] = useState([]);
  const [statistics, setStatistics] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [auditing, setAuditing] = useState(null);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [includeInactive, setIncludeInactive] = useState(false);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingControl, setEditingControl] = useState(null);

  const [form, setForm] = useState(emptyForm);


  async function loadControls() {
    setLoading(true);
    setError("");

    try {
      const [controlData, statsData] = await Promise.all([
        getControls(includeInactive),
        getControlStatistics(),
      ]);

      setControls(
        Array.isArray(controlData)
          ? controlData
          : []
      );

      setStatistics(statsData);
    } catch (e) {
      setError(
        getApiError(
          e,
          "Unable to load CTDISR controls."
        )
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadControls();
  }, [includeInactive]);


  function getControlId(control) {
    return (
      control?.control_id ??
      control?.id ??
      "—"
    );
  }


  function getControlDescription(control) {
    return (
      control?.control_description ??
      control?.description ??
      "No description available."
    );
  }


  function getControlTitle(control) {
    return (
      control?.title ??
      control?.name ??
      ""
    );
  }


  function isActive(control) {
    if (typeof control?.is_active === "boolean") {
      return control.is_active;
    }

    if (typeof control?.active === "boolean") {
      return control.active;
    }

    if (control?.status) {
      return (
        String(control.status).toLowerCase() ===
        "active"
      );
    }

    return true;
  }


  function openCreateDialog() {
    setEditingControl(null);
    setForm(emptyForm);
    setError("");
    setMessage("");
    setDialogOpen(true);
  }


  function openEditDialog(control) {
    setEditingControl(control);

    setForm({
      control_id:
        control?.control_id ??
        control?.id ??
        "",

      control_level:
        control?.control_level ??
        "CL1",

      control_description:
        control?.control_description ??
        control?.description ??
        "",

      interpretation:
        control?.interpretation ??
        "",

      pta_response:
        control?.pta_response ??
        control?.response ??
        "",

      pta_recommendations:
        control?.pta_recommendations ??
        control?.recommendation ??
        "",

      action_by:
        control?.action_by ??
        "",

      ntc_comments:
        control?.ntc_comments ??
        control?.comments ??
        "",

      source_document:
        control?.source_document ??
        "",
    });

    setError("");
    setMessage("");
    setDialogOpen(true);
  }


  function closeDialog() {
    if (saving) {
      return;
    }

    setDialogOpen(false);
    setEditingControl(null);
    setForm(emptyForm);
  }


  function handleChange(field) {
    return (event) => {
      setForm((previous) => ({
        ...previous,
        [field]: event.target.value,
      }));
    };
  }


  async function handleSave() {
    setSaving(true);
    setError("");
    setMessage("");

    try {
      if (editingControl) {
        const controlId =
          editingControl.control_id ??
          editingControl.id;

        await updateControl(
          controlId,
          {
            control_level:
              form.control_level,

            control_description:
              form.control_description,

            interpretation:
              form.interpretation,

            pta_response:
              form.pta_response,

            pta_recommendations:
              form.pta_recommendations,

            action_by:
              form.action_by,

            ntc_comments:
              form.ntc_comments,

            source_document:
              form.source_document,
          }
        );

        setMessage(
          `Control ${controlId} updated successfully.`
        );
      } else {
        await createControl({
          control_id:
            form.control_id,

          control_level:
            form.control_level,

          control_description:
            form.control_description,

          interpretation:
            form.interpretation,

          pta_response:
            form.pta_response,

          pta_recommendations:
            form.pta_recommendations,

          action_by:
            form.action_by,

          ntc_comments:
            form.ntc_comments,

          source_document:
            form.source_document,
        });

        setMessage(
          "Control created successfully."
        );
      }

      closeDialog();

      await loadControls();
    } catch (e) {
      setError(
        getApiError(
          e,
          editingControl
            ? "Unable to update control."
            : "Unable to create control."
        )
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleDeactivate(control) {
    const controlId =
      control?.control_id ??
      control?.id;

    if (!controlId) {
      setError(
        "Unable to determine the control ID."
      );
      return;
    }

    const confirmed = window.confirm(
      `Deactivate control ${controlId}?\n\nThis will mark the control as inactive.`
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await deactivateControl(controlId);

      setMessage(
        `Control ${controlId} deactivated successfully.`
      );

      await loadControls();
    } catch (e) {
      setError(
        getApiError(
          e,
          "Unable to deactivate control."
        )
      );
    }
  }


  async function handleAudit(control) {
    const controlId =
      control?.control_id ??
      control?.id;

    if (!controlId) {
      setError(
        "Unable to determine the control ID."
      );
      return;
    }

    setAuditing(controlId);
    setError("");
    setMessage("");

    try {
      await runAudit(
        controlId,
        {
          top_k: 5,
          max_new_tokens: 400,
        }
      );

      setMessage(
        `AI audit completed for control ${controlId}.`
      );
    } catch (e) {
      setError(
        getApiError(
          e,
          `Unable to audit control ${controlId}.`
        )
      );
    } finally {
      setAuditing(null);
    }
  }


  const totalControls =
    statistics?.total ??
    statistics?.total_controls ??
    controls.length;

  const activeControls =
    statistics?.active ??
    statistics?.active_controls ??
    controls.filter(isActive).length;

  const inactiveControls =
    statistics?.inactive ??
    statistics?.inactive_controls ??
    controls.filter(
      (control) => !isActive(control)
    ).length;


  return (
    <>
      <PageHeader
        eyebrow="COMPLIANCE"
        title="CTDISR Controls"
        subtitle="Manage PTA CTDISR controls, update control information, deactivate controls and run AI-assisted audits."
      />


      {message && (
        <Alert
          severity="success"
          sx={{ mb: 2 }}
          onClose={() => setMessage("")}
        >
          {message}
        </Alert>
      )}


      {error && (
        <Alert
          severity="error"
          sx={{ mb: 2 }}
          onClose={() => setError("")}
        >
          {error}
        </Alert>
      )}


      {/* Statistics */}

      <Stack
        direction={{
          xs: "column",
          sm: "row",
        }}
        spacing={1.5}
        sx={{ mb: 2 }}
      >
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography
              variant="caption"
              color="text.secondary"
            >
              TOTAL CONTROLS
            </Typography>

            <Typography
              variant="h5"
              sx={{ mt: 0.5 }}
            >
              {totalControls}
            </Typography>
          </CardContent>
        </Card>


        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography
              variant="caption"
              color="text.secondary"
            >
              ACTIVE
            </Typography>

            <Typography
              variant="h5"
              sx={{
                mt: 0.5,
                color: "success.main",
              }}
            >
              {activeControls}
            </Typography>
          </CardContent>
        </Card>


        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography
              variant="caption"
              color="text.secondary"
            >
              INACTIVE
            </Typography>

            <Typography
              variant="h5"
              sx={{
                mt: 0.5,
                color: "warning.main",
              }}
            >
              {inactiveControls}
            </Typography>
          </CardContent>
        </Card>
      </Stack>


      {/* Toolbar */}

      <Card sx={{ mb: 2 }}>
        <CardContent
          sx={{
            py: 1.5,
            "&:last-child": {
              pb: 1.5,
            },
          }}
        >
          <Stack
            direction={{
              xs: "column",
              md: "row",
            }}
            spacing={1.2}
            alignItems={{
              xs: "stretch",
              md: "center",
            }}
          >
            <Box sx={{ flex: 1 }}>
              <Typography fontWeight={750}>
                Control register
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                {controls.length} control
                {controls.length === 1
                  ? ""
                  : "s"} displayed
              </Typography>
            </Box>


            <TextField
              select
              label="View"
              value={
                includeInactive
                  ? "all"
                  : "active"
              }
              onChange={(event) =>
                setIncludeInactive(
                  event.target.value ===
                    "all"
                )
              }
              sx={{ minWidth: 160 }}
            >
              <MenuItem value="active">
                Active controls
              </MenuItem>

              <MenuItem value="all">
                All controls
              </MenuItem>
            </TextField>


            <Tooltip title="Refresh controls">
              <IconButton
                onClick={loadControls}
                disabled={loading}
              >
                <RefreshOutlined />
              </IconButton>
            </Tooltip>


            {isAdmin && (
              <Button
                variant="contained"
                startIcon={
                  <AddOutlined />
                }
                onClick={
                  openCreateDialog
                }
              >
                Add Control
              </Button>
            )}
          </Stack>
        </CardContent>
      </Card>


      {/* Control list */}

      <Card>
        <CardContent sx={{ p: 0 }}>
          {loading ? (
            <Box
              sx={{
                minHeight: 260,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <CircularProgress
                size={30}
              />
            </Box>
          ) : controls.length === 0 ? (
            <Box
              sx={{
                minHeight: 260,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexDirection: "column",
                p: 4,
              }}
            >
              <Typography fontWeight={700}>
                No controls found
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mt: 0.5 }}
              >
                No CTDISR controls are
                available for the selected
                view.
              </Typography>
            </Box>
          ) : (
            <Box>
              {controls.map(
                (control, index) => {
                  const controlId =
                    getControlId(control);

                  const active =
                    isActive(control);

                  return (
                    <Box key={controlId}>
                      <Box
                        sx={{
                          p: {
                            xs: 2,
                            md: 2.4,
                          },
                        }}
                      >
                        <Stack
                          direction={{
                            xs: "column",
                            lg: "row",
                          }}
                          spacing={2}
                        >
                          {/* Information */}

                          <Box
                            sx={{
                              flex: 1,
                              minWidth: 0,
                            }}
                          >
                            <Stack
                              direction="row"
                              spacing={1}
                              alignItems="center"
                              sx={{
                                mb: 0.8,
                              }}
                            >
                              <Typography
                                fontWeight={800}
                                sx={{
                                  color:
                                    "primary.main",
                                }}
                              >
                                {controlId}
                              </Typography>

                              <Chip
                                size="small"
                                label={
                                  active
                                    ? "Active"
                                    : "Inactive"
                                }
                                color={
                                  active
                                    ? "success"
                                    : "warning"
                                }
                                variant="outlined"
                              />
                            </Stack>


                            {getControlTitle(
                              control
                            ) && (
                              <Typography
                                fontWeight={700}
                                sx={{
                                  mb: 0.5,
                                }}
                              >
                                {getControlTitle(
                                  control
                                )}
                              </Typography>
                            )}


                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{
                                maxWidth: 1000,
                                lineHeight: 1.6,
                              }}
                            >
                              {getControlDescription(
                                control
                              )}
                            </Typography>


                            {control.control_level && (
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{
                                  display:
                                    "block",
                                  mt: 1,
                                }}
                              >
                                Level:{" "}
                                {
                                  control.control_level
                                }
                              </Typography>
                            )}
                          </Box>


                          {/* Actions */}

                          <Stack
                            direction="row"
                            spacing={0.7}
                            alignItems="center"
                            flexWrap="wrap"
                          >
                            <Tooltip title="View control">
                              <IconButton
                                size="small"
                                component={Link}
                                to={`/controls/${encodeURIComponent(
                                  controlId
                                )}`}
                                sx={{
                                  border:
                                    "1px solid rgba(255,255,255,.08)",
                                  borderRadius: 1.5,
                                }}
                              >
                                <VisibilityOutlined fontSize="small" />
                              </IconButton>
                            </Tooltip>


                            {isAdmin && (
                              <Tooltip title="Edit control">
                                <span>
                                  <IconButton
                                    size="small"
                                    onClick={() =>
                                      openEditDialog(
                                        control
                                      )
                                    }
                                    disabled={
                                      !active
                                    }
                                    sx={{
                                      border:
                                        "1px solid rgba(255,255,255,.08)",
                                      borderRadius: 1.5,
                                    }}
                                  >
                                    <EditOutlined fontSize="small" />
                                  </IconButton>
                                </span>
                              </Tooltip>
                            )}


                            {isAdmin && (
                              <Tooltip
                                title={
                                  active
                                    ? "Deactivate control"
                                    : "Control already inactive"
                                }
                              >
                                <span>
                                  <IconButton
                                    size="small"
                                    color="warning"
                                    onClick={() =>
                                      handleDeactivate(
                                        control
                                      )
                                    }
                                    disabled={
                                      !active
                                    }
                                    sx={{
                                      border:
                                        "1px solid rgba(234,179,8,.18)",
                                      borderRadius: 1.5,
                                    }}
                                  >
                                    <BlockOutlined fontSize="small" />
                                  </IconButton>
                                </span>
                              </Tooltip>
                            )}


                            <Button
                              size="small"
                              variant="outlined"
                              startIcon={
                                auditing ===
                                controlId ? (
                                  <CircularProgress
                                    size={14}
                                  />
                                ) : (
                                  <PlayArrowOutlined />
                                )
                              }
                              disabled={
                                !active ||
                                auditing ===
                                  controlId
                              }
                              onClick={() =>
                                handleAudit(
                                  control
                                )
                              }
                            >
                              {auditing ===
                              controlId
                                ? "Auditing..."
                                : "Run AI Audit"}
                            </Button>
                          </Stack>
                        </Stack>
                      </Box>


                      {index <
                        controls.length -
                          1 && (
                        <Divider />
                      )}
                    </Box>
                  );
                }
              )}
            </Box>
          )}
        </CardContent>
      </Card>


      {/* Create / Edit dialog */}

      <Dialog
        open={dialogOpen}
        onClose={closeDialog}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          {editingControl
            ? `Edit Control ${
                editingControl.control_id ??
                editingControl.id ??
                ""
              }`
            : "Create CTDISR Control"}
        </DialogTitle>


        <DialogContent dividers>
          <Stack
            spacing={2}
            sx={{ pt: 0.5 }}
          >
            {!editingControl && (
              <TextField
                label="Control ID"
                value={
                  form.control_id
                }
                onChange={handleChange(
                  "control_id"
                )}
                fullWidth
                required
                placeholder="e.g. 4.4"
              />
            )}


            <TextField
              label="Control Level"
              value={
                form.control_level
              }
              onChange={handleChange(
                "control_level"
              )}
              fullWidth
              required
            />


            <TextField
              label="Control Description"
              value={
                form.control_description
              }
              onChange={handleChange(
                "control_description"
              )}
              fullWidth
              required
              multiline
              minRows={3}
            />


            <TextField
              label="Interpretation"
              value={
                form.interpretation
              }
              onChange={handleChange(
                "interpretation"
              )}
              fullWidth
              multiline
              minRows={3}
            />


            <TextField
              label="PTA Response"
              value={
                form.pta_response
              }
              onChange={handleChange(
                "pta_response"
              )}
              fullWidth
              multiline
              minRows={3}
            />


            <TextField
              label="PTA Recommendations"
              value={
                form.pta_recommendations
              }
              onChange={handleChange(
                "pta_recommendations"
              )}
              fullWidth
              multiline
              minRows={3}
            />


            <TextField
              label="Action By"
              value={
                form.action_by
              }
              onChange={handleChange(
                "action_by"
              )}
              fullWidth
            />


            <TextField
              label="NTC Comments"
              value={
                form.ntc_comments
              }
              onChange={handleChange(
                "ntc_comments"
              )}
              fullWidth
              multiline
              minRows={3}
            />


            <TextField
              label="Source Document"
              value={
                form.source_document
              }
              onChange={handleChange(
                "source_document"
              )}
              fullWidth
            />
          </Stack>
        </DialogContent>


        <DialogActions>
          <Button
            onClick={closeDialog}
            disabled={saving}
          >
            Cancel
          </Button>


          <Button
            variant="contained"
            onClick={handleSave}
            disabled={
              saving ||
              !form.control_id ||
              !form.control_level ||
              !form.control_description
            }
            startIcon={
              saving ? (
                <CircularProgress
                  size={15}
                />
              ) : null
            }
          >
            {saving
              ? "Saving..."
              : editingControl
              ? "Save Changes"
              : "Create Control"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

