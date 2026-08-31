import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import AppLayout from "../layouts/AppLayout";
import LoginPage from "../pages/LoginPage";
import DashboardPage from "../pages/DashboardPage";
import ControlsPage from "../pages/ControlsPage";
import ControlDetailsPage from "../pages/ControlDetailsPage";
import AuditsPage from "../pages/AuditsPage";
import AuditDetailsPage from "../pages/AuditDetailsPage";
import DocumentsPage from "../pages/DocumentsPage";
import UsersPage from "../pages/UsersPage";

function RequireAuth({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function RequireAdmin({ children }) {
  const { isAdmin } = useAuth();
  return isAdmin ? children : <Navigate to="/dashboard" replace />;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/controls" element={<ControlsPage />} />
        <Route path="/controls/:controlId" element={<ControlDetailsPage />} />
        <Route path="/audits" element={<AuditsPage />} />
        <Route path="/audits/:auditId" element={<AuditDetailsPage />} />
        <Route
          path="/users"
          element={
            <RequireAdmin>
              <UsersPage />
            </RequireAdmin>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}