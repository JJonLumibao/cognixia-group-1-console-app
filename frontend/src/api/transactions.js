import apiClient from "./client";

export function getTransactions() {
  return apiClient.get("/transactions").then((res) => res.data);
}

export function createTransaction(payload) {
  return apiClient.post("/transactions", payload).then((res) => res.data);
}

export function transferFunds(payload) {
  return apiClient.post("/transactions/transfer", payload).then((res) => res.data);
}
