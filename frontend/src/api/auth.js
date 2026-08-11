import apiClient from "./client";

export function registerUser({ email, password, role }) {
  return apiClient.post("/auth/register", { email, password, role }).then((res) => res.data);
}

export function loginUser({ email, password }) {
  return apiClient.post("/auth/login", { email, password }).then((res) => res.data);
}
