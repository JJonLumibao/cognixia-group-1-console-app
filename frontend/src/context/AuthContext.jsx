import { createContext, useContext, useMemo, useState } from "react";
import { loginUser, registerUser } from "../api/auth";
import { decodeJwt } from "../utils/jwt";

const AuthContext = createContext(null);

function readStoredUser() {
  const token = localStorage.getItem("access_token");
  if (!token) return null;

  const claims = decodeJwt(token);
  if (!claims) return null;

  return {
    id: claims.sub,
    email: claims.email,
    roles: claims.roles || [],
    token,
  };
}

function storeTokens(data) {
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  const claims = decodeJwt(data.access_token);
  return {
    id: claims?.sub,
    email: claims?.email,
    roles: claims?.roles || [],
    token: data.access_token,
  };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser);

  const login = async ({ email, password }) => {
    const data = await loginUser({ email, password });
    const nextUser = storeTokens(data);
    setUser(nextUser);
    return nextUser;
  };

  const register = async ({ email, password, role }) => {
    // Registering now logs the user in immediately (backend returns a TokenResponse).
    const data = await registerUser({ email, password, role });
    const nextUser = storeTokens(data);
    setUser(nextUser);
    return nextUser;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      hasRole: (...roles) => !!user && roles.some((r) => user.roles.includes(r)),
      login,
      register,
      logout,
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
