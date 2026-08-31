import { useEffect, useMemo, useRef, useState } from "react";

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
  InputAdornment,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";

import {
  CheckCircleOutline,
  CloudUploadOutlined,
  DeleteOutline,
  DescriptionOutlined,
  ErrorOutline,
  FolderOutlined,
  InfoOutlined,
  RefreshOutlined,
  SearchOutlined,
  StorageOutlined,
  VisibilityOutlined,
} from "@mui/icons-material";

import PageHeader from "../components/PageHeader";

import {
  deleteDocument,
  getDocument,
  getDocuments,
  uploadDocument,
} from "../services/documents.service";

import { getApiError } from "../services/api";

/*
 * Backend values must remain:
 *
 * advisory
 * policy
 * ctdisr
 * asset
 */
const categories = [
  {
    value: "all",
    label: "All categories",
  },
  {
    value: "policy",
    label: "Policies",
  },
  {
    value: "advisory",
    label: "Advisories",
  },
  {
    value: "ctdisr",
    label: "CTDISR",
  },
  {
    value: "asset",
    label: "Assets",
  },
];

const uploadCategories = categories.filter(
  (item) => item.value !== "all"
);

const statusOptions = [
  {
    value: "all",
    label: "All statuses",
  },
  {
    value: "processed",
    label: "Processed",
  },
  {
    value: "processing",
    label: "Processing",
  },
  {
    value: "failed",
    label: "Failed",
  },
];

/* ---------------------------------------------------------
   Helpers
--------------------------------------------------------- */

function normalizeDocuments(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.documents)) {
    return payload.documents;
  }

  if (Array.isArray(payload?.items)) {
    return payload.items;
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  return [];
}

function getDocumentId(document) {
  return (
    document?.document_id ??
    document?.id ??
    document?.uuid ??
    document?.documentId ??
    ""
  );
}

function getDocumentName(document) {
  return (
    document?.filename ??
    document?.file_name ??
    document?.name ??
    document?.original_filename ??
    "Unnamed document"
  );
}

function getDocumentCategory(document) {
  return String(
    document?.category ??
      document?.document_category ??
      "unknown"
  ).toLowerCase();
}

function getDocumentStatus(document) {
  return String(
    document?.status ??
      document?.processing_status ??
      document?.state ??
      "processed"
  ).toLowerCase();
}

function getCategoryLabel(category) {
  const found = categories.find(
    (item) => item.value === category
  );

  return found?.label || category || "Unknown";
}

function getStatusLabel(status) {
  if (status === "processed") return "Processed";
  if (status === "processing") return "Processing";
  if (status === "failed") return "Failed";

  return status
    ? status.charAt(0).toUpperCase() + status.slice(1)
    : "Unknown";
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
  });
}

function formatBytes(bytes) {
  if (
    bytes === undefined ||
    bytes === null ||
    Number.isNaN(Number(bytes))
  ) {
    return "—";
  }

  const value = Number(bytes);

  if (value < 1024) {
    return `${value} B`;
  }

  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }

  if (value < 1024 * 1024 * 1024) {
    return `${(value / (1024 * 1024)).toFixed(1)} MB`;
  }

  return `${(value / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

/* ---------------------------------------------------------
   Status chip
--------------------------------------------------------- */

function DocumentStatusChip({ status }) {
  const normalized = getDocumentStatus({
    status,
  });

  let color = "default";
  let icon = <InfoOutlined sx={{ fontSize: 14 }} />;

  if (normalized === "processed" || normalized === "complete") {
    color = "success";
    icon = <CheckCircleOutline sx={{ fontSize: 14 }} />;
  }

  if (
    normalized === "processing" ||
    normalized === "pending"
  ) {
    color = "warning";
    icon = (
      <CircularProgress
        size={12}
        thickness={5}
        color="inherit"
      />
    );
  }

  if (
    normalized === "failed" ||
    normalized === "error"
  ) {
    color = "error";
    icon = <ErrorOutline sx={{ fontSize: 14 }} />;
  }

  return (
    <Chip
      size="small"
      icon={icon}
      label={getStatusLabel(normalized)}
      color={color}
      variant="outlined"
      sx={{
        height: 25,
        fontSize: 10,
        fontWeight: 700,
        "& .MuiChip-icon": {
          ml: 0.7,
        },
      }}
    />
  );
}

/* ---------------------------------------------------------
   Main page
--------------------------------------------------------- */

export default function DocumentsPage() {
  const input = useRef(null);

  /* Upload state */
  const [category, setCategory] = useState("policy");
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [busy, setBusy] = useState(false);

  /* Document list */
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  /* Filters */
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] =
    useState("all");
  const [statusFilter, setStatusFilter] =
    useState("all");

  /* Messages */
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  /* Details dialog */
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] =
    useState(null);
  const [detailsLoading, setDetailsLoading] =
    useState(false);

  /* Delete dialog */
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] =
    useState(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  /* -------------------------------------------------------
     Load documents
  ------------------------------------------------------- */

  async function loadDocuments(showLoader = true) {
    if (showLoader) {
      setLoading(true);
    }

    setError("");

    try {
      const result = await getDocuments();

      setDocuments(normalizeDocuments(result));
    } catch (e) {
      setError(
        getApiError(
          e,
          "Unable to load documents."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  /* -------------------------------------------------------
     Upload
  ------------------------------------------------------- */

  async function upload() {
    if (!file || busy) return;

    setBusy(true);
    setMessage("");
    setError("");
    setProgress(0);

    try {
      const result = await uploadDocument(
        file,
        category,
        (event) => {
          if (event.total) {
            setProgress(
              Math.round(
                (event.loaded / event.total) * 100
              )
            );
          }
        }
      );

      setMessage(
        result?.message ||
          "Document uploaded and processed successfully."
      );

      setFile(null);

      if (input.current) {
        input.current.value = "";
      }

      /*
       * Refresh the table after successful upload.
       */
      await loadDocuments(false);
    } catch (e) {
      setError(
        getApiError(
          e,
          "Document upload failed."
        )
      );
    } finally {
      setBusy(false);
      setProgress(0);
    }
  }

  /* -------------------------------------------------------
     Details
  ------------------------------------------------------- */

  async function openDetails(document) {
    const documentId = getDocumentId(document);

    setDetailsOpen(true);
    setSelectedDocument(document);

    if (!documentId) {
      return;
    }

    setDetailsLoading(true);

    try {
      const result = await getDocument(documentId);

      setSelectedDocument(result);
    } catch (e) {
      setError(
        getApiError(
          e,
          "Unable to load document details."
        )
      );
    } finally {
      setDetailsLoading(false);
    }
  }

  /* -------------------------------------------------------
     Delete
  ------------------------------------------------------- */

  function askDelete(document) {
    setDocumentToDelete(document);
    setDeleteOpen(true);
  }

  async function confirmDelete() {
    if (!documentToDelete || deleteBusy) {
      return;
    }

    const documentId =
      getDocumentId(documentToDelete);

    if (!documentId) {
      setError("Document ID is missing.");
      return;
    }

    setDeleteBusy(true);
    setError("");
    setMessage("");

    try {
      const result = await deleteDocument(
        documentId
      );

      setMessage(
        result?.message ||
          "Document deleted successfully."
      );

      setDeleteOpen(false);
      setDocumentToDelete(null);

      await loadDocuments(false);
    } catch (e) {
      setError(
        getApiError(
          e,
          "Unable to delete the document."
        )
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  /* -------------------------------------------------------
     Filtered documents
  ------------------------------------------------------- */

  const filteredDocuments = useMemo(() => {
    const query = search.trim().toLowerCase();

    return documents.filter((document) => {
      const name = getDocumentName(document)
        .toLowerCase();

      const documentCategory =
        getDocumentCategory(document);

      const documentStatus =
        getDocumentStatus(document);

      const matchesSearch =
        !query ||
        name.includes(query) ||
        String(
          getDocumentId(document)
        )
          .toLowerCase()
          .includes(query);

      const matchesCategory =
        categoryFilter === "all" ||
        documentCategory === categoryFilter;

      const matchesStatus =
        statusFilter === "all" ||
        documentStatus === statusFilter;

      return (
        matchesSearch &&
        matchesCategory &&
        matchesStatus
      );
    });
  }, [
    documents,
    search,
    categoryFilter,
    statusFilter,
  ]);

  /* -------------------------------------------------------
     Statistics
  ------------------------------------------------------- */

  const statistics = useMemo(() => {
    return {
      total: documents.length,

      policies: documents.filter(
        (document) =>
          getDocumentCategory(document) ===
          "policy"
      ).length,

      advisories: documents.filter(
        (document) =>
          getDocumentCategory(document) ===
          "advisory"
      ).length,

      ctdisr: documents.filter(
        (document) =>
          getDocumentCategory(document) ===
          "ctdisr"
      ).length,

      assets: documents.filter(
        (document) =>
          getDocumentCategory(document) ===
          "asset"
      ).length,

      processed: documents.filter((document) =>
        ["processed", "complete"].includes(
          getDocumentStatus(document)
        )
      ).length,

      processing: documents.filter((document) =>
        ["processing", "pending"].includes(
          getDocumentStatus(document)
        )
      ).length,

      failed: documents.filter((document) =>
        ["failed", "error"].includes(
          getDocumentStatus(document)
        )
      ).length,
    };
  }, [documents]);

  /* -------------------------------------------------------
     Render
  ------------------------------------------------------- */

  return (
    <>
      <PageHeader
        eyebrow="KNOWLEDGE BASE"
        title="Document Management"
        subtitle="Manage the source material used by the PTA CTDISR compliance knowledge engine."
      />

      {/* Messages */}
      <Stack spacing={1.2} sx={{ mb: 2 }}>
        {message && (
          <Alert
            severity="success"
            onClose={() => setMessage("")}
          >
            {message}
          </Alert>
        )}

        {error && (
          <Alert
            severity="error"
            onClose={() => setError("")}
          >
            {error}
          </Alert>
        )}
      </Stack>

      {/* ---------------------------------------------------
          Statistics
      --------------------------------------------------- */}

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, 1fr)",
            lg: "repeat(4, 1fr)",
          },
          gap: 1.5,
          mb: 2,
        }}
      >
        <Metric
          icon={<StorageOutlined />}
          label="Total documents"
          value={statistics.total}
        />

        <Metric
          icon={<CheckCircleOutline />}
          label="Processed"
          value={statistics.processed}
          tone="success"
        />

        <Metric
          icon={<FolderOutlined />}
          label="Knowledge categories"
          value={
            [
              statistics.policies,
              statistics.advisories,
              statistics.ctdisr,
              statistics.assets,
            ].filter((value) => value > 0).length
          }
        />

        <Metric
          icon={<ErrorOutline />}
          label="Processing issues"
          value={
            statistics.processing +
            statistics.failed
          }
          tone={
            statistics.processing +
              statistics.failed >
            0
              ? "warning"
              : "success"
          }
        />
      </Box>

      {/* ---------------------------------------------------
          Upload card
      --------------------------------------------------- */}

      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: { xs: 2, md: 2.5 } }}>
          <Stack
            direction={{
              xs: "column",
              md: "row",
            }}
            spacing={2}
            alignItems={{
              xs: "stretch",
              md: "center",
            }}
          >
            <Box sx={{ flex: 1 }}>
              <Stack
                direction="row"
                spacing={1.2}
                alignItems="center"
              >
                <CloudUploadOutlined
                  sx={{
                    color: "primary.main",
                  }}
                />

                <Box>
                  <Typography
                    fontWeight={750}
                    sx={{ fontSize: 14 }}
                  >
                    Upload knowledge document
                  </Typography>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                  >
                    Upload policies, advisories,
                    CTDISR material or asset
                    documentation for processing.
                  </Typography>
                </Box>
              </Stack>
            </Box>

            <TextField
              select
              label="Category"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value)
              }
              sx={{
                minWidth: {
                  xs: "100%",
                  md: 190,
                },
              }}
              disabled={busy}
            >
              {uploadCategories.map((item) => (
                <MenuItem
                  key={item.value}
                  value={item.value}
                >
                  {item.label}
                </MenuItem>
              ))}
            </TextField>

            <Button
              variant="contained"
              startIcon={<CloudUploadOutlined />}
              onClick={() => input.current?.click()}
              disabled={busy}
              sx={{
                minWidth: 150,
                height: 40,
              }}
            >
              Choose file
            </Button>
          </Stack>

          <input
            ref={input}
            type="file"
            hidden
            accept=".pdf,.doc,.docx,.xls,.xlsx"
            onChange={(event) =>
              setFile(
                event.target.files?.[0] || null
              )
            }
          />

          {file && (
            <Paper
              variant="outlined"
              sx={{
                mt: 2,
                p: 1.4,
                background:
                  "rgba(34,197,94,.025)",
              }}
            >
              <Stack
                direction={{
                  xs: "column",
                  sm: "row",
                }}
                spacing={1.5}
                alignItems={{
                  xs: "stretch",
                  sm: "center",
                }}
              >
                <DescriptionOutlined
                  sx={{
                    color: "primary.main",
                  }}
                />

                <Box sx={{ flex: 1 }}>
                  <Typography
                    fontWeight={650}
                  >
                    {file.name}
                  </Typography>

                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    {formatBytes(file.size)}
                    {" · "}
                    {getCategoryLabel(category)}
                  </Typography>
                </Box>

                <Button
                  variant="contained"
                  onClick={upload}
                  disabled={busy}
                  startIcon={
                    busy ? (
                      <CircularProgress
                        size={14}
                        color="inherit"
                      />
                    ) : (
                      <CloudUploadOutlined />
                    )
                  }
                >
                  {busy
                    ? "Processing..."
                    : "Upload & Process"}
                </Button>
              </Stack>

              {busy && (
                <Box sx={{ mt: 1.5 }}>
                  <LinearProgress
                    variant="determinate"
                    value={progress}
                  />

                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{
                      display: "block",
                      mt: 0.6,
                    }}
                  >
                    {progress}% uploaded — processing
                    may continue on the server.
                  </Typography>
                </Box>
              )}
            </Paper>
          )}
        </CardContent>
      </Card>

      {/* ---------------------------------------------------
          Document table
      --------------------------------------------------- */}

      <Card>
        <CardContent
          sx={{
            p: 0,
            "&:last-child": {
              pb: 0,
            },
          }}
        >
          {/* Toolbar */}

          <Box
            sx={{
              p: 2,
              borderBottom:
                "1px solid rgba(255,255,255,.07)",
            }}
          >
            <Stack
              direction={{
                xs: "column",
                md: "row",
              }}
              spacing={1}
              alignItems={{
                xs: "stretch",
                md: "center",
              }}
            >
              <TextField
                size="small"
                placeholder="Search documents..."
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                sx={{
                  flex: 1,
                  minWidth: 220,
                }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchOutlined
                        sx={{
                          fontSize: 18,
                          color:
                            "text.secondary",
                        }}
                      />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                select
                size="small"
                label="Category"
                value={categoryFilter}
                onChange={(event) =>
                  setCategoryFilter(
                    event.target.value
                  )
                }
                sx={{ minWidth: 150 }}
              >
                {categories.map((item) => (
                  <MenuItem
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                select
                size="small"
                label="Status"
                value={statusFilter}
                onChange={(event) =>
                  setStatusFilter(
                    event.target.value
                  )
                }
                sx={{ minWidth: 145 }}
              >
                {statusOptions.map((item) => (
                  <MenuItem
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </MenuItem>
                ))}
              </TextField>

              <Tooltip title="Refresh documents">
                <IconButton
                  onClick={() =>
                    loadDocuments()
                  }
                  disabled={loading}
                  sx={{
                    border:
                      "1px solid rgba(255,255,255,.08)",
                    borderRadius: 1.5,
                  }}
                >
                  <RefreshOutlined
                    sx={{ fontSize: 19 }}
                  />
                </IconButton>
              </Tooltip>
            </Stack>
          </Box>

          {/* Table */}

          <TableContainer>
            <Table
              size="small"
              sx={{
                minWidth: 780,
              }}
            >
              <TableHead>
                <TableRow>
                  <TableCell>
                    Document
                  </TableCell>

                  <TableCell>
                    Category
                  </TableCell>

                  <TableCell>
                    Status
                  </TableCell>

                  <TableCell>
                    Uploaded
                  </TableCell>

                  <TableCell>
                    Size
                  </TableCell>

                  <TableCell align="right">
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      align="center"
                      sx={{ py: 6 }}
                    >
                      <CircularProgress
                        size={26}
                      />

                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 1 }}
                      >
                        Loading documents...
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : filteredDocuments.length ===
                  0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      align="center"
                      sx={{ py: 7 }}
                    >
                      <DescriptionOutlined
                        sx={{
                          fontSize: 34,
                          color:
                            "text.secondary",
                          opacity: 0.55,
                        }}
                      />

                      <Typography
                        fontWeight={650}
                        sx={{ mt: 1 }}
                      >
                        No documents found
                      </Typography>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        Try changing the search or
                        filters, or upload a new
                        document.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredDocuments.map(
                    (document, index) => {
                      const id =
                        getDocumentId(document);

                      const name =
                        getDocumentName(document);

                      const documentCategory =
                        getDocumentCategory(
                          document
                        );

                      const status =
                        getDocumentStatus(
                          document
                        );

                      const uploadedAt =
                        document?.uploaded_at ??
                        document?.upload_date ??
                        document?.created_at ??
                        document?.createdAt;

                      const size =
                        document?.file_size ??
                        document?.size ??
                        document?.size_bytes;

                      return (
                        <TableRow
                          key={
                            id ||
                            `${name}-${index}`
                          }
                          hover
                        >
                          <TableCell>
                            <Stack
                              direction="row"
                              spacing={1.2}
                              alignItems="center"
                            >
                              <Box
                                sx={{
                                  width: 32,
                                  height: 32,
                                  borderRadius: 1.3,
                                  display: "grid",
                                  placeItems:
                                    "center",
                                  background:
                                    "rgba(34,197,94,.08)",
                                  color:
                                    "primary.main",
                                }}
                              >
                                <DescriptionOutlined
                                  sx={{
                                    fontSize: 17,
                                  }}
                                />
                              </Box>

                              <Box
                                sx={{
                                  minWidth: 0,
                                }}
                              >
                                <Typography
                                  fontWeight={650}
                                  noWrap
                                  sx={{
                                    maxWidth: 330,
                                  }}
                                >
                                  {name}
                                </Typography>

                                {id && (
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                    noWrap
                                    sx={{
                                      display:
                                        "block",
                                      maxWidth: 330,
                                    }}
                                  >
                                    ID: {id}
                                  </Typography>
                                )}
                              </Box>
                            </Stack>
                          </TableCell>

                          <TableCell>
                            <Chip
                              label={getCategoryLabel(
                                documentCategory
                              )}
                              size="small"
                              variant="outlined"
                              sx={{
                                height: 24,
                                fontSize: 9.5,
                                fontWeight: 700,
                              }}
                            />
                          </TableCell>

                          <TableCell>
                            <DocumentStatusChip
                              status={status}
                            />
                          </TableCell>

                          <TableCell>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                            >
                              {formatDate(
                                uploadedAt
                              )}
                            </Typography>
                          </TableCell>

                          <TableCell>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                            >
                              {formatBytes(size)}
                            </Typography>
                          </TableCell>

                          <TableCell align="right">
                            <Stack
                              direction="row"
                              spacing={0.4}
                              justifyContent="flex-end"
                            >
                              <Tooltip title="View details">
                                <IconButton
                                  size="small"
                                  onClick={() =>
                                    openDetails(
                                      document
                                    )
                                  }
                                >
                                  <VisibilityOutlined
                                    sx={{
                                      fontSize: 18,
                                    }}
                                  />
                                </IconButton>
                              </Tooltip>

                              <Tooltip title="Delete document">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() =>
                                    askDelete(
                                      document
                                    )
                                  }
                                >
                                  <DeleteOutline
                                    sx={{
                                      fontSize: 18,
                                    }}
                                  />
                                </IconButton>
                              </Tooltip>
                            </Stack>
                          </TableCell>
                        </TableRow>
                      );
                    }
                  )
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Footer */}

          {!loading &&
            filteredDocuments.length > 0 && (
              <Box
                sx={{
                  px: 2,
                  py: 1.2,
                  borderTop:
                    "1px solid rgba(255,255,255,.06)",
                }}
              >
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Showing{" "}
                  <strong>
                    {filteredDocuments.length}
                  </strong>{" "}
                  of{" "}
                  <strong>
                    {documents.length}
                  </strong>{" "}
                  documents
                </Typography>
              </Box>
            )}
        </CardContent>
      </Card>

      {/* ---------------------------------------------------
          Details dialog
      --------------------------------------------------- */}

      <Dialog
        open={detailsOpen}
        onClose={() =>
          setDetailsOpen(false)
        }
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
          >
            <InfoOutlined
              sx={{ color: "primary.main" }}
            />

            <Typography
              component="span"
              fontWeight={750}
            >
              Document Details
            </Typography>
          </Stack>
        </DialogTitle>

        <DialogContent dividers>
          {detailsLoading ? (
            <Box
              sx={{
                py: 5,
                display: "grid",
                placeItems: "center",
              }}
            >
              <CircularProgress />
            </Box>
          ) : selectedDocument ? (
            <Stack spacing={1.8}>
              <DetailRow
                label="Filename"
                value={getDocumentName(
                  selectedDocument
                )}
              />

              <DetailRow
                label="Document ID"
                value={
                  getDocumentId(
                    selectedDocument
                  ) || "—"
                }
              />

              <DetailRow
                label="Category"
                value={getCategoryLabel(
                  getDocumentCategory(
                    selectedDocument
                  )
                )}
              />

              <DetailRow
                label="Status"
                value={
                  <DocumentStatusChip
                    status={getDocumentStatus(
                      selectedDocument
                    )}
                  />
                }
              />

              <DetailRow
                label="File type"
                value={
                  selectedDocument?.file_type ??
                  selectedDocument?.mime_type ??
                  selectedDocument?.content_type ??
                  "—"
                }
              />

              <DetailRow
                label="File size"
                value={formatBytes(
                  selectedDocument?.file_size ??
                    selectedDocument?.size ??
                    selectedDocument?.size_bytes
                )}
              />

              <DetailRow
                label="Uploaded"
                value={formatDate(
                  selectedDocument?.uploaded_at ??
                    selectedDocument?.upload_date ??
                    selectedDocument?.created_at
                )}
              />

              <Divider />

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Additional metadata
                </Typography>

                <Paper
                  variant="outlined"
                  sx={{
                    mt: 0.8,
                    p: 1.4,
                    maxHeight: 220,
                    overflow: "auto",
                    background:
                      "rgba(255,255,255,.015)",
                  }}
                >
                  <Typography
                    component="pre"
                    sx={{
                      m: 0,
                      whiteSpace:
                        "pre-wrap",
                      wordBreak:
                        "break-word",
                      fontFamily:
                        "ui-monospace, SFMono-Regular, Menlo, monospace",
                      fontSize: 10,
                      color:
                        "text.secondary",
                    }}
                  >
                    {JSON.stringify(
                      selectedDocument,
                      null,
                      2
                    )}
                  </Typography>
                </Paper>
              </Box>
            </Stack>
          ) : (
            <Typography color="text.secondary">
              No document details available.
            </Typography>
          )}
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() =>
              setDetailsOpen(false)
            }
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* ---------------------------------------------------
          Delete confirmation
      --------------------------------------------------- */}

      <Dialog
        open={deleteOpen}
        onClose={() => {
          if (!deleteBusy) {
            setDeleteOpen(false);
          }
        }}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>
          Delete document?
        </DialogTitle>

        <DialogContent>
          <Typography
            variant="body2"
            color="text.secondary"
          >
            You are about to permanently remove:
          </Typography>

          <Typography
            fontWeight={700}
            sx={{ mt: 1 }}
          >
            {documentToDelete
              ? getDocumentName(
                  documentToDelete
                )
              : ""}
          </Typography>

          <Typography
            variant="body2"
            color="error.main"
            sx={{ mt: 1.5 }}
          >
            This action cannot be undone.
          </Typography>
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() =>
              setDeleteOpen(false)
            }
            disabled={deleteBusy}
          >
            Cancel
          </Button>

          <Button
            color="error"
            variant="contained"
            startIcon={
              deleteBusy ? (
                <CircularProgress
                  size={14}
                  color="inherit"
                />
              ) : (
                <DeleteOutline />
              )
            }
            onClick={confirmDelete}
            disabled={deleteBusy}
          >
            {deleteBusy
              ? "Deleting..."
              : "Delete document"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

/* ---------------------------------------------------------
   Metric component
--------------------------------------------------------- */

function Metric({
  icon,
  label,
  value,
  tone = "default",
}) {
  const iconColor =
    tone === "success"
      ? "success.main"
      : tone === "warning"
      ? "warning.main"
      : "primary.main";

  return (
    <Card>
      <CardContent
        sx={{
          p: 1.8,
          "&:last-child": {
            pb: 1.8,
          },
        }}
      >
        <Stack
          direction="row"
          spacing={1.3}
          alignItems="center"
        >
          <Box
            sx={{
              width: 34,
              height: 34,
              borderRadius: 1.5,
              display: "grid",
              placeItems: "center",
              color: iconColor,
              background:
                "rgba(34,197,94,.07)",
            }}
          >
            {icon}
          </Box>

          <Box>
            <Typography
              variant="caption"
              color="text.secondary"
            >
              {label}
            </Typography>

            <Typography
              sx={{
                mt: 0.1,
                fontSize: 20,
                fontWeight: 750,
                lineHeight: 1.1,
              }}
            >
              {value}
            </Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}

/* ---------------------------------------------------------
   Details row
--------------------------------------------------------- */

function DetailRow({ label, value }) {
  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns:
          "130px minmax(0, 1fr)",
        gap: 2,
        alignItems: "center",
      }}
    >
      <Typography
        variant="caption"
        color="text.secondary"
        fontWeight={700}
      >
        {label}
      </Typography>

      <Box
        sx={{
          minWidth: 0,
          overflow: "hidden",
        }}
      >
        {typeof value === "string" ? (
          <Typography
            variant="body2"
            sx={{
              wordBreak: "break-word",
            }}
          >
            {value}
          </Typography>
        ) : (
          value
        )}
      </Box>
    </Box>
  );
}