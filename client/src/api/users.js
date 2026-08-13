import apiClient from "./client";

// ADMIN only.
export function getUsers() {
  return apiClient.get("/users").then((res) => res.data);
}
