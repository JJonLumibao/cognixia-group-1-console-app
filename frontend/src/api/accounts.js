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
