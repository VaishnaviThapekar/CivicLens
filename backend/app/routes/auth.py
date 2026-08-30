import uuid
import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from app.services.notification_engine import get_user_notifications, send_notification

router = APIRouter(prefix="/api/auth", tags=["auth"])

USERS_DB = {
  "citizen@civiclens.org": {
    "user_id": "usr-citizen-001",
    "email": "citizen@civiclens.org",
    "password_hash": "hashed_password123",
    "full_name": "Alex Morgan",
    "phone": "+1 555 0192834",
    "role": "Citizen",
    "is_email_verified": True,
    "profile_photo_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex",
    "preferred_language": "English",
    "default_location": {"city": "Central District", "ward": "Ward 63", "lat": 19.9975, "lng": 73.7898},
    "notifications": [
      {"id": "n1", "title": "Welcome to CivicLens!", "message": "Your account is active.", "read": False, "date": "Just now"}
    ],
    "contribution_history": [
      {"action": "Account Created", "points": 50, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    ],
    "my_reports_count": 24
  }
}

TOKENS_DB = {}
VERIFICATION_TOKENS = {}
RESET_TOKENS = {}

ROLE_PERMISSIONS = {
  "Citizen": ["report_issue", "view_own_reports", "confirm_resolution", "track_status"],
  "Volunteer": ["report_issue", "view_all_public_reports", "verify_ground_issue", "add_field_notes"],
  "Officer": ["view_assigned_tickets", "accept_ticket", "upload_repair_evidence", "mark_resolved"],
  "Supervisor": ["view_ward_analytics", "audit_contractor_scores", "review_fake_flags", "export_dossier"],
  "Administrator": ["configure_system", "manage_users", "manage_gis_boundaries", "all_permissions"]
}

class RegisterRequest(BaseModel):
  email: str
  password: str
  full_name: str
  phone: Optional[str] = "+91 9876543210"
  role: Optional[str] = "Citizen"
  preferred_language: Optional[str] = "English"

class LoginRequest(BaseModel):
  email: str
  password: str

class GoogleOAuthRequest(BaseModel):
  id_token: Optional[str] = "google_token_sample"
  email: Optional[str] = "citizen@civiclens.org"
  full_name: Optional[str] = "Vaishnavi"

class RefreshTokenRequest(BaseModel):
  refresh_token: str

class ForgotPasswordRequest(BaseModel):
  email: str

class ResetPasswordRequest(BaseModel):
  reset_token: str
  new_password: str

class UpdateProfileRequest(BaseModel):
  full_name: Optional[str] = None
  phone: Optional[str] = None
  profile_photo_url: Optional[str] = None
  preferred_language: Optional[str] = None
  default_location: Optional[dict] = None

class OTPRequest(BaseModel):
  phone: str
  otp: Optional[str] = "123456"

@router.post("/register")
def register_user(req: RegisterRequest):
  if req.email in USERS_DB:
    raise HTTPException(status_code=400, detail="Email already registered")

  user_id = f"usr-{uuid.uuid4().hex[:8]}"
  verification_token = f"ver-{uuid.uuid4().hex[:12]}"
  VERIFICATION_TOKENS[verification_token] = req.email

  user = {
    "user_id": user_id,
    "email": req.email,
    "password_hash": f"hashed_{req.password}",
    "full_name": req.full_name,
    "phone": req.phone,
    "role": req.role if req.role in ROLE_PERMISSIONS else "Citizen",
    "is_email_verified": False,
    "profile_photo_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=" + user_id,
    "preferred_language": req.preferred_language or "English",
    "default_location": {"city": "Central District", "ward": "Ward 63", "lat": 19.9975, "lng": 73.7898},
    "notifications": [],
    "contribution_history": [
      {"action": "Account Created", "points": 50, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    ],
    "my_reports_count": 0
  }

  USERS_DB[req.email] = user
  return {
    "message": "User registered successfully. Please verify your email.",
    "user_id": user_id,
    "email": req.email,
    "verification_token": verification_token
  }

@router.get("/verify-email")
def verify_email(token: str):
  email = VERIFICATION_TOKENS.get(token)
  if not email or email not in USERS_DB:
    raise HTTPException(status_code=400, detail="Invalid or expired verification token")

  USERS_DB[email]["is_email_verified"] = True
  del VERIFICATION_TOKENS[token]
  return {"message": "Email verified successfully!", "email": email}

@router.post("/login")
def login_user(req: LoginRequest):
  user = USERS_DB.get(req.email)
  if not user or user["password_hash"] != f"hashed_{req.password}":
    raise HTTPException(status_code=401, detail="Invalid credentials")

  access_token = f"jwt-access-{uuid.uuid4().hex[:16]}"
  refresh_token = f"jwt-refresh-{uuid.uuid4().hex[:16]}"

  TOKENS_DB[access_token] = req.email
  TOKENS_DB[refresh_token] = req.email

  return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "token_type": "bearer",
    "user": {
      "user_id": user["user_id"],
      "full_name": user["full_name"],
      "email": user["email"],
      "role": user["role"],
      "permissions": ROLE_PERMISSIONS.get(user["role"], [])
    }
  }

@router.post("/google")
@router.post("/oauth/google")
def google_oauth(req: Optional[GoogleOAuthRequest] = None):
  email = req.email if req and req.email else "citizen@civiclens.org"
  full_name = req.full_name if req and req.full_name else "Alex Morgan"

  if email not in USERS_DB:
    user_id = f"usr-g-{uuid.uuid4().hex[:8]}"
    USERS_DB[email] = {
      "user_id": user_id,
      "email": email,
      "password_hash": "oauth_google",
      "full_name": full_name,
      "phone": "+91 9876543210",
      "role": "Citizen",
      "is_email_verified": True,
      "profile_photo_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=" + email,
      "preferred_language": "English",
      "default_location": {"city": "Central District", "ward": "Ward 63", "lat": 19.9975, "lng": 73.7898},
      "notifications": [],
      "contribution_history": [{"action": "Logged in via Google OAuth", "points": 10}],
      "my_reports_count": 0
    }

  user = USERS_DB[email]
  access_token = f"jwt-access-{uuid.uuid4().hex[:16]}"
  refresh_token = f"jwt-refresh-{uuid.uuid4().hex[:16]}"
  TOKENS_DB[access_token] = email

  return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "user": user
  }

@router.post("/otp/send")
def send_otp(req: OTPRequest):
  return {"message": f"OTP sent to {req.phone}", "otp_sent": True}

@router.post("/otp/verify")
def verify_otp(req: OTPRequest):
  if req.otp != "123456":
    raise HTTPException(status_code=400, detail="Invalid OTP")

  access_token = f"jwt-access-otp-{uuid.uuid4().hex[:16]}"
  return {
    "message": "OTP verified successfully!",
    "access_token": access_token,
    "user": USERS_DB["citizen@civiclens.org"]
  }

@router.post("/refresh")
def refresh_token(req: RefreshTokenRequest):
  email = TOKENS_DB.get(req.refresh_token)
  if not email or email not in USERS_DB:
    raise HTTPException(status_code=401, detail="Invalid refresh token")

  new_access_token = f"jwt-access-{uuid.uuid4().hex[:16]}"
  TOKENS_DB[new_access_token] = email
  return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
  if req.email not in USERS_DB:
    return {"message": "If the email exists, a password reset link has been generated."}

  reset_token = f"rst-{uuid.uuid4().hex[:12]}"
  RESET_TOKENS[reset_token] = req.email
  return {"message": "Password reset token generated.", "reset_token": reset_token}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
  email = RESET_TOKENS.get(req.reset_token)
  if not email or email not in USERS_DB:
    raise HTTPException(status_code=400, detail="Invalid or expired reset token")

  USERS_DB[email]["password_hash"] = f"hashed_{req.new_password}"
  del RESET_TOKENS[req.reset_token]
  return {"message": "Password reset successfully. Please login with your new password."}

@router.get("/profile")
def get_user_profile(authorization: Optional[str] = Header(None)):
  token = authorization.replace("Bearer ", "") if authorization else None
  email = TOKENS_DB.get(token, "citizen@civiclens.org")
  user = USERS_DB.get(email, USERS_DB["citizen@civiclens.org"])

  return {
    "profile": user,
    "permissions": ROLE_PERMISSIONS.get(user["role"], ROLE_PERMISSIONS["Citizen"])
  }

@router.put("/profile")
def update_user_profile(req: UpdateProfileRequest, authorization: Optional[str] = Header(None)):
  token = authorization.replace("Bearer ", "") if authorization else None
  email = TOKENS_DB.get(token, "citizen@civiclens.org")
  if email not in USERS_DB:
    raise HTTPException(status_code=401, detail="Unauthorized")

  user = USERS_DB[email]
  if req.full_name: user["full_name"] = req.full_name
  if req.phone: user["phone"] = req.phone
  if req.profile_photo_url: user["profile_photo_url"] = req.profile_photo_url
  if req.preferred_language: user["preferred_language"] = req.preferred_language
  if req.default_location: user["default_location"] = req.default_location

  return {"message": "Profile updated successfully", "profile": user}

@router.get("/notifications")
def get_notifications(authorization: Optional[str] = Header(None)):
  token = authorization.replace("Bearer ", "") if authorization else None
  email = TOKENS_DB.get(token, "citizen@civiclens.org")
  return {
    "notifications": get_user_notifications(email),
    "authority_alerts": get_user_notifications("authority_command")
  }

@router.get("/roles")
def get_rbac_roles():
  return {
    "roles": list(ROLE_PERMISSIONS.keys()),
    "permissions_matrix": ROLE_PERMISSIONS
  }
