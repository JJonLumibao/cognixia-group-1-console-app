import apiClient from "./client";

export function getCustomers() {
  return apiClient.get("/customers").then((res) => res.data);
}

export function getCustomer(customerId) {
  return apiClient.get(`/customers/${customerId}`).then((res) => res.data);
}

export function createCustomer(payload) {
  return apiClient.post("/customers", payload).then((res) => res.data);
}

export function updateCustomer(customerId, payload) {
  return apiClient.put(`/customers/${customerId}`, payload).then((res) => res.data);
}

export function deactivateCustomer(customerId) {
  return apiClient.delete(`/customers/${customerId}`).then((res) => res.data);
}
