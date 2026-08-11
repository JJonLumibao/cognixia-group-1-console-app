import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { STAFF_ROLES } from "../constants/roles";

export default function HomePage() {
  const { isAuthenticated, hasRole } = useAuth();

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (hasRole(...STAFF_ROLES)) return <Navigate to="/dashboard" replace />;
  return <Navigate to="/portal" replace />;
}
