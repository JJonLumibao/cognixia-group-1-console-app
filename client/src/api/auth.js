import apiClient from "./client";

export function registerUser({ email, password, role, branchId }) {
  // Register now logs the user in directly and returns a TokenResponse.
  // branch_id is required by the backend for every role.
  return apiClient
    .post("/auth/register", { email, password, role, branch_id: branchId })
    .then((res) => res.data);
}

export function loginUser({ email, password }) {
  // Login uses OAuth2PasswordRequestForm on the backend, so it must be sent
  // as application/x-www-form-urlencoded with a "username" field (not JSON).
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);

  return apiClient
    .post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    })
    .then((res) => res.data);
}
