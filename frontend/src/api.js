// frontend/src/api.js
const BASE = "http://localhost:8001";

export const fetchAllDeals   = () =>
  fetch(`${BASE}/deals`).then(r => r.json());

export const fetchDeal       = (id) =>
  fetch(`${BASE}/deal/${id}`).then(r => r.json());

export const fetchCoach      = (id) =>
  fetch(`${BASE}/coach/${id}`, { method: "POST" }).then(r => r.json());

export const fetchBenchmarks = () =>
  fetch(`${BASE}/benchmarks`).then(r => r.json());
