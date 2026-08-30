const API_BASE_URL = "http://localhost:8000/api";

export async function fetchComplaints() {
  const res = await fetch(`${API_BASE_URL}/complaints/`);
  if (!res.ok) throw new Error("Failed to fetch complaints");
  return res.json();
}

export async function submitComplaint(payload: any) {
  const res = await fetch(`${API_BASE_URL}/complaints/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to submit complaint");
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE_URL}/officer/stats`);
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function verifyResolution(payload: any) {
  const res = await fetch(`${API_BASE_URL}/verification/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Verification failed");
  return res.json();
}

export async function fetchPredictiveRisks() {
  const res = await fetch(`${API_BASE_URL}/intelligence/predictive-risks`);
  if (!res.ok) throw new Error("Failed to fetch predictive risks");
  return res.json();
}

// User Auth & Profile APIs
export async function registerUser(payload: any) {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Registration failed");
  return res.json();
}

export async function loginUser(payload: any) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json();
}

export async function fetchUserProfile() {
  const res = await fetch(`${API_BASE_URL}/auth/profile`);
  if (!res.ok) throw new Error("Failed to fetch user profile");
  return res.json();
}

export async function fetchRBACRoles() {
  const res = await fetch(`${API_BASE_URL}/auth/roles`);
  if (!res.ok) throw new Error("Failed to fetch roles");
  return res.json();
}
