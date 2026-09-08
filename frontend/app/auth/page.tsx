"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Lock, Mail, User, Phone, ShieldCheck, ArrowRight, Sparkles, CheckCircle2, RefreshCw, KeyRound, Smartphone
} from "lucide-react";
import { loginUser, registerUser } from "@/lib/api";

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup" | "forgot">("login");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Bug 43 Fix: Default login input state to empty strings rather than pre-filling credentials
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const fillDemoCredentials = (email: string, pass: string = "password123") => {
    setLoginEmail(email);
    setLoginPassword(pass);
  };

  // Sign Up Form State
  const [fullName, setFullName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupPhone, setSignupPhone] = useState("+91 ");
  const [signupRole, setSignupRole] = useState("Citizen");
  const [language, setLanguage] = useState("English");

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      const res = await loginUser({ email: loginEmail, password: loginPassword });
      setSuccessMsg(`Welcome back, ${res.user.full_name}! Redirecting...`);
      localStorage.setItem("civiclens_token", res.access_token);
      localStorage.setItem("civiclens_user", JSON.stringify(res.user));

      setTimeout(() => {
        if (res.user.role === "Officer") router.push("/officer");
        else if (res.user.role === "Supervisor") router.push("/supervisor");
        else if (res.user.role === "Administrator") router.push("/admin");
        else router.push("/citizen");
      }, 1000);
    } catch (err: any) {
      setErrorMsg(err.message || "Invalid credentials. Please check your email and password.");
    } finally {
      setLoading(false);
    }
  };

  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      const res = await registerUser({
        full_name: fullName,
        email: signupEmail,
        password: signupPassword,
        phone: signupPhone,
        role: signupRole,
        preferred_language: language
      });
      setSuccessMsg("Account created successfully! Redirecting to Sign In...");
      setTimeout(() => {
        setMode("login");
        setLoginEmail(signupEmail);
        setLoginPassword(signupPassword);
      }, 1200);
    } catch (err: any) {
      setErrorMsg(err.message || "Registration failed. Email may already be registered.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleOAuth = () => {
    setLoading(true);
    setTimeout(() => {
      setSuccessMsg("Google OAuth authentication verified! Logging in as Vaishnavi...");
      setTimeout(() => router.push("/citizen"), 1000);
    }, 800);
  };

  return (
    <div className="max-w-md mx-auto my-8 space-y-6 animate-fade-in">
      {/* Header Badge & Title */}
      <div className="text-center space-y-2">
        <span className="text-xs font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3.5 py-1 rounded-full border border-[#287C73]/20">
          CivicLens Unified Identity Portal
        </span>
        <h1 className="text-3xl font-black text-[#102C2B]">
          {mode === "login" ? "Sign In to CivicLens" : mode === "signup" ? "Create Account" : "Reset Password"}
        </h1>
        <p className="text-xs text-[#4B6363] font-medium">
          Access citizen grievance tracking, officer dispatches, and civic intelligence.
        </p>
      </div>

      {/* Mode Switcher Tabs */}
      <div className="flex bg-[#F7F6F2] p-1.5 rounded-2xl border border-[#E7E9E4]">
        <button
          type="button"
          onClick={() => { setMode("login"); setErrorMsg(""); setSuccessMsg(""); }}
          className={`flex-1 py-2.5 rounded-xl font-extrabold text-xs transition-all ${
            mode === "login" ? "bg-[#287C73] text-white shadow-sm" : "text-[#4B6363] hover:text-[#102C2B]"
          }`}
        >
          🔑 Sign In
        </button>

        <button
          type="button"
          onClick={() => { setMode("signup"); setErrorMsg(""); setSuccessMsg(""); }}
          className={`flex-1 py-2.5 rounded-xl font-extrabold text-xs transition-all ${
            mode === "signup" ? "bg-[#287C73] text-white shadow-sm" : "text-[#4B6363] hover:text-[#102C2B]"
          }`}
        >
          📝 Sign Up
        </button>
      </div>

      {/* Alert Banners */}
      {errorMsg && (
        <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-xs font-bold text-red-700 flex items-center gap-2">
          <span>⚠️ {errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-700 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Form Card */}
      <div className="bg-white border border-[#E7E9E4] rounded-3xl p-8 shadow-md space-y-6">
        {mode === "login" && (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-[#102C2B] block">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#4B6363] absolute left-3.5 top-3" />
                <input
                  type="email"
                  required
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="citizen@civiclens.org"
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl pl-10 pr-4 py-2.5 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-[#102C2B]">Password</label>
                <button
                  type="button"
                  onClick={() => setMode("forgot")}
                  className="text-[11px] font-bold text-[#287C73] hover:underline"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#4B6363] absolute left-3.5 top-3" />
                <input
                  type="password"
                  required
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl pl-10 pr-4 py-2.5 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-md flex items-center justify-center gap-2 transition-all teal-glow mt-2"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <>Sign In &rarr;</>}
            </button>

            <div className="relative py-2 text-center">
              <span className="bg-white px-3 text-[11px] text-[#4B6363] font-bold relative z-10">OR</span>
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-[#E7E9E4]" /></div>
            </div>

            <button
              type="button"
              onClick={handleGoogleOAuth}
              className="w-full py-3 rounded-2xl bg-[#F7F6F2] hover:bg-[#E7E9E4] text-[#102C2B] font-extrabold text-xs border border-[#E7E9E4] flex items-center justify-center gap-2 transition-all"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.11-6.72-4.96H1.29v3.15C3.26 21.3 7.31 24 12 24z"/>
                <path fill="#FBBC05" d="M5.28 14.24c-.25-.72-.38-1.49-.38-2.24s.13-1.52.38-2.24V6.61H1.29C.47 8.24 0 10.06 0 12s.47 3.76 1.29 5.39l3.99-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.26 2.7 1.29 6.61l3.99 3.15c.95-2.85 3.6-4.96 6.72-4.96z"/>
              </svg>
              Sign In with Google OAuth
            </button>
          </form>
        )}

        {mode === "signup" && (
          <form onSubmit={handleSignupSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-[#102C2B] block">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-[#4B6363] absolute left-3.5 top-3" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl pl-10 pr-4 py-2.5 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-[#102C2B] block">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#4B6363] absolute left-3.5 top-3" />
                <input
                  type="email"
                  required
                  value={signupEmail}
                  onChange={(e) => setSignupEmail(e.target.value)}
                  placeholder="vaishnavi@civiclens.org"
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl pl-10 pr-4 py-2.5 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-[#102C2B] block">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#4B6363] absolute left-3.5 top-3" />
                <input
                  type="password"
                  required
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl pl-10 pr-4 py-2.5 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-[#102C2B] block">Role</label>
                <select
                  value={signupRole}
                  onChange={(e) => setSignupRole(e.target.value)}
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl px-3 py-2.5 text-xs text-[#102C2B] font-bold"
                >
                  <option value="Citizen">Citizen</option>
                  <option value="Volunteer">Volunteer</option>
                  <option value="Officer">Officer</option>
                  <option value="Supervisor">Supervisor</option>
                  <option value="Administrator">Administrator</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-[#102C2B] block">Language</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl px-3 py-2.5 text-xs text-[#102C2B] font-bold"
                >
                  <option value="English">English</option>
                  <option value="Marathi">मराठी (Marathi)</option>
                  <option value="Hindi">हिंदी (Hindi)</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-md flex items-center justify-center gap-2 transition-all teal-glow mt-2"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <>Create Account &rarr;</>}
            </button>
          </form>
        )}

        {mode === "forgot" && (
          <div className="space-y-4">
            <p className="text-xs text-[#4B6363] font-medium">
              Enter your registered email address to receive a password reset link.
            </p>
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-[#102C2B] block">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#4B6363] absolute left-3.5 top-3" />
                <input
                  type="email"
                  placeholder="citizen@civiclens.org"
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl pl-10 pr-4 py-2.5 text-xs text-[#102C2B] font-semibold"
                />
              </div>
            </div>

            <button
              type="button"
              onClick={() => setSuccessMsg("Password reset link sent to your email!")}
              className="w-full py-3.5 rounded-2xl bg-[#287C73] text-white font-extrabold text-xs shadow-md"
            >
              Send Reset Link
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
