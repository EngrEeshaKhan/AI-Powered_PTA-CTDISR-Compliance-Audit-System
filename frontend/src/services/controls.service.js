import api from "./api";

/**
 * Get CTDISR controls.
 *
 * Backend:
 * GET /api/v1/ctdisr/controls
 *
 * includeInactive = false:
 * returns active controls only.
 *
 * includeInactive = true:
 * returns active + inactive controls.
 */
export async function getControls(includeInactive = false) {
  const { data } = await api.get("/ctdisr/controls", {
    params: {
      include_inactive: includeInactive,
    },
  });

  return data;
}

/**
 * Get a single CTDISR control.
 *
 * Backend:
 * GET /api/v1/ctdisr/controls/{control_id}
 */
export async function getControl(controlId) {
  const { data } = await api.get(
    `/ctdisr/controls/${encodeURIComponent(controlId)}`
  );

  return data;
}

/**
 * Get CTDISR control statistics.
 *
 * Backend:
 * GET /api/v1/ctdisr/controls/statistics
 */
export async function getControlStatistics() {
  const { data } = await api.get(
    "/ctdisr/controls/statistics"
  );

  return data;
}

/**
 * Create a new CTDISR control.
 *
 * Backend:
 * POST /api/v1/ctdisr/controls
 */
export async function createControl(payload) {
  const { data } = await api.post(
    "/ctdisr/controls",
    payload
  );

  return data;
}

/**
 * Update an existing CTDISR control.
 *
 * Backend:
 * PUT /api/v1/ctdisr/controls/{control_id}
 */
export async function updateControl(controlId, payload) {
  const { data } = await api.put(
    `/ctdisr/controls/${encodeURIComponent(controlId)}`,
    payload
  );

  return data;
}

/**
 * Deactivate a CTDISR control.
 *
 * Backend:
 * DELETE /api/v1/ctdisr/controls/{control_id}
 *
 * IMPORTANT:
 * Your backend describes this DELETE endpoint as
 * "Deactivate Control", not physical deletion.
 */
export async function deactivateControl(controlId) {
  const { data } = await api.delete(
    `/ctdisr/controls/${encodeURIComponent(controlId)}`
  );

  return data;
}

/**
 * Run AI audit for a CTDISR control.
 *
 * Backend:
 * POST /api/v1/ctdisr/controls/{control_id}/audit
 */
export async function runAudit(controlId, params = {}) {
  const { data } = await api.post(
    `/ctdisr/controls/${encodeURIComponent(controlId)}/audit`,
    null,
    {
      params,
    }
  );

  return data;
}