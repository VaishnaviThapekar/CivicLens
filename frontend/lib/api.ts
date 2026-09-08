// Bug 38 Fix: Configurable API base URL with production environment variable support
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// Bug 40 Fix: Strict TypeScript interfaces replacing 'any' types
export interface LocationDataPayload {
  lat: number;
  lng: number;
  address?: string;
  city?: string;
  ward?: string;
  zone?: string;
  road_name?: string;
  nearest_landmark?: string;
}

export interface ComplaintCreatePayload {
  title?: string | null;
  description: string;
  category?: string | null;
  media_type?: string;
  image_url?: string | null;
  video_url?: string | null;
  voice_transcript?: string | null;
  audio_base64?: string | null;
  language?: string | null;
  timestamp?: string | null;
  location: LocationDataPayload;
}

export interface ResolutionEvidencePayload {
  complaint_id: string;
  officer_id?: string | null;
  officer_notes?: string | null;
  evidence_image_url: string;
  gps_lat?: number | null;
  gps_lng?: number | null;
  timestamp?: string | null;
}

export interface AuthRegisterPayload {
  name?: string;
  full_name?: string;
  email: string;
  phone?: string;
  password?: string;
  role?: string;
  language_preference?: string;
  preferred_language?: string;
}

export interface AuthLoginPayload {
  email: string;
  password?: string;
  otp?: string;
}

// Bug 39 Fix: Helper function to extract detailed backend validation errors
async function handleResponseError(res: Response, fallbackMsg: string): Promise<never> {
  let errorDetail = fallbackMsg;
  try {
    const data = await res.json();
    errorDetail = data.detail || data.message || data.error || fallbackMsg;
  } catch {
    errorDetail = res.statusText || fallbackMsg;
  }
  throw new Error(typeof errorDetail === "string" ? errorDetail : JSON.stringify(errorDetail));
}

export async function fetchComplaints() {
  const res = await fetch(`${API_BASE_URL}/complaints/`);
  if (!res.ok) await handleResponseError(res, "Failed to fetch complaints");
  return res.json();
}

export async function submitComplaint(payload: ComplaintCreatePayload) {
  const res = await fetch(`${API_BASE_URL}/complaints/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) await handleResponseError(res, "Failed to submit complaint");
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE_URL}/officer/stats`);
  if (!res.ok) await handleResponseError(res, "Failed to fetch stats");
  return res.json();
}

// Bug 37 Fix: Calls /verification/verify endpoint (aligned with backend route handler)
export async function verifyResolution(payload: ResolutionEvidencePayload) {
  const res = await fetch(`${API_BASE_URL}/verification/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) await handleResponseError(res, "Verification failed");
  return res.json();
}

export async function fetchPredictiveRisks() {
  const res = await fetch(`${API_BASE_URL}/intelligence/predictive-risks`);
  if (!res.ok) await handleResponseError(res, "Failed to fetch predictive risks");
  return res.json();
}

// User Auth & Profile APIs
export async function registerUser(payload: AuthRegisterPayload) {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) await handleResponseError(res, "Registration failed");
  return res.json();
}

export async function loginUser(payload: AuthLoginPayload) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) await handleResponseError(res, "Login failed");
  return res.json();
}

export async function fetchUserProfile() {
  const res = await fetch(`${API_BASE_URL}/auth/profile`);
  if (!res.ok) await handleResponseError(res, "Failed to fetch user profile");
  return res.json();
}

export async function fetchRBACRoles() {
  const res = await fetch(`${API_BASE_URL}/auth/roles`);
  if (!res.ok) await handleResponseError(res, "Failed to fetch roles");
  return res.json();
}
