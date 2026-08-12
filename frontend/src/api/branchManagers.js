import apiClient from "./client";

// ADMIN only.
export function getBranches() {
  return apiClient.get("/branch-managers/branches").then((res) => res.data);
}

// ADMIN only.
export function createBranch(payload) {
  return apiClient.post("/branch-managers/branches", payload).then((res) => res.data);
}

// ADMIN only.
export function updateBranchManager(branchCode, managerId) {
  return apiClient
    .patch(`/branch-managers/${branchCode}/manager`, { manager_id: managerId })
    .then((res) => res.data);
}

// BRANCH_MANAGER only — scoped to the branch the logged-in manager owns.
export function getBranchPerformance() {
  return apiClient.get("/branch-managers/branch-performance").then((res) => res.data);
}

// BRANCH_MANAGER only — scoped to the branch the logged-in manager owns.
export function getStaffMetrics() {
  return apiClient.get("/branch-managers/staff-metrics").then((res) => res.data);
}
