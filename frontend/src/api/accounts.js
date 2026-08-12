import apiClient from "./client";

export function getAccounts({ branchId, minBalance } = {}) {
  return apiClient
    .get("/accounts", {
      params: {
        branch_id: branchId || undefined,
        min_balance: minBalance || undefined,
      },
    })
    .then((res) => res.data);
}

export function createAccount(payload) {
  return apiClient.post("/accounts", payload).then((res) => res.data);
}

// CUSTOMER (own accounts only) / ADMIN.
export function updateAccountStatus(accountId, active) {
  return apiClient.patch(`/accounts/${accountId}/status`, { active }).then((res) => res.data);
}
