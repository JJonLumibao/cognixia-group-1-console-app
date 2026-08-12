import apiClient from "./client";

// Staff only (TELLER / ADMIN).
export function getTransactions() {
  return apiClient.get("/transactions").then((res) => res.data);
}

// Staff only (TELLER / ADMIN).
export function depositMoney({ accountId, amount }) {
  return apiClient
    .post("/transactions/deposit", { account_id: accountId, amount })
    .then((res) => res.data);
}

// Staff only (TELLER / ADMIN).
export function withdrawMoney({ accountId, amount }) {
  return apiClient
    .post("/transactions/withdraw", { account_id: accountId, amount })
    .then((res) => res.data);
}

// Customer (own accounts only) / ADMIN.
export function transferFunds(payload) {
  return apiClient.post("/transactions/transfer", payload).then((res) => res.data);
}
