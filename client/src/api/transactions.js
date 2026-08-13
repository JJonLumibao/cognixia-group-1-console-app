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

// CUSTOMER / TELLER / BRANCH_MANAGER / ADMIN.
// request_type must be exactly "Deposit", "Withdrawal", or "Transfer".
export function createTransactionRequest(payload) {
  return apiClient.post("/transactions/requests", payload).then((res) => res.data);
}

// TELLER / BRANCH_MANAGER / ADMIN. Staff without a branch assigned get a 400.
export function getTransactionRequests() {
  return apiClient.get("/transactions/requests").then((res) => res.data);
}

// TELLER / BRANCH_MANAGER / ADMIN.
export function approveTransactionRequest(requestId) {
  return apiClient.patch(`/transactions/requests/${requestId}/approve`).then((res) => res.data);
}

// TELLER / BRANCH_MANAGER / ADMIN.
export function rejectTransactionRequest(requestId) {
  return apiClient.patch(`/transactions/requests/${requestId}/reject`).then((res) => res.data);
}
