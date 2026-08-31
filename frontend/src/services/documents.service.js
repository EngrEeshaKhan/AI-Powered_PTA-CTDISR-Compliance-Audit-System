import api from "./api";

/**
 * Upload a document and let the backend process it.
 *
 * Backend:
 * POST /api/v1/uploads/
 */
export async function uploadDocument(
  file,
  category,
  onUploadProgress
) {
  const form = new FormData();

  form.append("category", category);
  form.append("file", file);

  const { data } = await api.post("/uploads/", form, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress,
  });

  return data;
}

/**
 * Get all uploaded documents.
 *
 * Backend:
 * GET /api/v1/uploads/
 */
export async function getDocuments() {
  const { data } = await api.get("/uploads/");
  return data;
}

/**
 * Get details for one document.
 *
 * Backend:
 * GET /api/v1/uploads/{document_id}
 */
export async function getDocument(documentId) {
  const { data } = await api.get(
    `/uploads/${encodeURIComponent(documentId)}`
  );

  return data;
}

/**
 * Delete one uploaded document.
 *
 * Backend:
 * DELETE /api/v1/uploads/{document_id}
 */
export async function deleteDocument(documentId) {
  const { data } = await api.delete(
    `/uploads/${encodeURIComponent(documentId)}`
  );

  return data;
}