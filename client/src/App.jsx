import { Routes, Route } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import CustomerPortalPage from "./pages/CustomerPortalPage";
import ManagerDashboardPage from "./pages/ManagerDashboardPage";
import NotFoundPage from "./pages/NotFoundPage";
import { STAFF_ROLES } from "./constants/roles";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/portal"
        element={
          <ProtectedRoute roles={["CUSTOMER"]}>
            <CustomerPortalPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute roles={STAFF_ROLES}>
            <ManagerDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
