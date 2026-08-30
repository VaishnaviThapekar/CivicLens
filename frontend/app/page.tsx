"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Lock, Mail, User, ShieldCheck, ArrowRight, Sparkles, CheckCircle2, RefreshCw, KeyRound, Globe, Compass,
  Camera, MapPin, Eye, Activity, ShieldAlert, Award, LogOut, Building2, Layers, TrendingUp
} from "lucide-react";
import MapVisualizer from "@/components/MapVisualizer";
import { loginUser, registerUser } from "@/lib/api";

export default function RootLandingAuthPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [userProfile, setUserProfile] = useState<any>(null);

  // Sign In Form State
  const [loginEmail, setLoginEmail] = useState("citizen@civiclens.org");
  const [loginPassword, setLoginPassword] = useState("password123");

  // Sign Up Form State
  const [fullName, setFullName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupRole, setSignupRole] = useState("Citizen");

  useEffect(() => {
    const authFlag = localStorage.getItem("civiclens_authenticated");
    const storedUser = localStorage.getItem("civiclens_user");
    if (authFlag === "true") {
      setIsAuthenticated(true);
      if (storedUser) setUserProfile(JSON.parse(storedUser));
    }
  }, []);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      const res = await loginUser({ email: loginEmail, password: loginPassword });
      setSuccessMsg(`Authentication Successful! Unlocking City Dashboard...`);
      localStorage.setItem("civiclens_token", res.access_token);
      localStorage.setItem("civiclens_user", JSON.stringify(res.user));
      localStorage.setItem("civiclens_authenticated", "true");
      setUserProfile(res.user);

      setTimeout(() => {
        setIsAuthenticated(true);
      }, 700);
    } catch (err: any) {
      setErrorMsg("Invalid credentials. Please check your email and password.");
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
      await registerUser({
        full_name: fullName,
        email: signupEmail,
        password: signupPassword,
        role: signupRole
      });
      setSuccessMsg("Account created! Redirecting to Sign In...");
      setTimeout(() => {
        setMode("login");
        setLoginEmail(signupEmail);
        setLoginPassword(signupPassword);
      }, 900);
    } catch (err: any) {
      setErrorMsg("Registration failed. Email may already be registered.");
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem("civiclens_authenticated");
    localStorage.removeItem("civiclens_user");
    localStorage.removeItem("civiclens_token");
    setIsAuthenticated(false);
    setUserProfile(null);
  };

  // 1. UNIQUE ENHANCED LANDING GATEWAY WITH CITY VIEWS & SIGN IN GATE
  if (!isAuthenticated) {
    return (
      <div className="space-y-12 pb-16 animate-fade-in">
        {/* City View Hero Header */}
        <section className="relative overflow-hidden bg-white text-[#102C2B] border border-[#E7E9E4] rounded-3xl p-8 sm:p-12 shadow-md">
          {/* Animated City Grid Vector Graphic Background */}
          <div className="absolute inset-0 opacity-10 pointer-events-none">
            <svg className="w-full h-full" viewBox="0 0 1000 500" preserveAspectRatio="none">
              <path d="M 0,400 L 200,300 L 400,380 L 600,260 L 800,340 L 1000,220 V 500 H 0 Z" fill="#287C73" />
              <circle cx="200" cy="300" r="12" fill="#287C73" className="animate-ping" />
              <circle cx="600" cy="260" r="10" fill="#F3B83F" className="animate-bounce" />
              <circle cx="800" cy="340" r="14" fill="#D94F4F" className="animate-ping" />
            </svg>
          </div>

          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left: City Telemetry & Value Proposition */}
            <div className="lg:col-span-6 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#287C73]/10 text-[#287C73] border border-[#287C73]/20 text-xs font-extrabold">
                <Building2 className="w-4 h-4 text-[#287C73]" /> Central District Urban Grid Portal
              </div>

              <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight text-[#102C2B]">
                See Your City. <br />
                <span className="text-[#287C73]">Make It Better.</span>
              </h1>

              <p className="text-xs sm:text-sm text-[#4B6363] font-medium leading-relaxed max-w-lg">
                AI-powered civic intelligence turning citizen report photos, multilingual voice notes, and IoT sensor feeds into verified, SLA-enforced municipal action.
              </p>

              {/* City Metric Tickers */}
              <div className="grid grid-cols-3 gap-3 pt-2">
                <div className="bg-[#F7F6F2] border border-[#E7E9E4] p-3 rounded-2xl">
                  <span className="text-[10px] uppercase font-bold text-[#4B6363] block">ACTIVE INCIDENTS</span>
                  <strong className="text-lg font-black text-[#102C2B]">184 Live</strong>
                </div>

                <div className="bg-[#F7F6F2] border border-[#E7E9E4] p-3 rounded-2xl">
                  <span className="text-[10px] uppercase font-bold text-[#4B6363] block">CRITICAL P1</span>
                  <strong className="text-lg font-black text-[#D94F4F]">42 Priority</strong>
                </div>

                <div className="bg-[#F7F6F2] border border-[#E7E9E4] p-3 rounded-2xl">
                  <span className="text-[10px] uppercase font-bold text-[#4B6363] block">AI VERIFIED</span>
                  <strong className="text-lg font-black text-[#10B981]">73% Pass Rate</strong>
                </div>
              </div>
            </div>

            {/* Right: Sign In Gate Card */}
            <div className="lg:col-span-6 bg-white text-[#102C2B] border border-[#E7E9E4] rounded-3xl p-7 shadow-2xl space-y-5">
              <div className="text-center space-y-1">
                <span className="text-[10px] font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3 py-0.5 rounded-full border border-[#287C73]/20">
                  🔐 AUTHENTICATION GATEWAY
                </span>
                <h2 className="text-2xl font-black text-[#102C2B]">Sign In to Enter City Platform</h2>
              </div>

              {/* Mode Switcher Tabs */}
              <div className="flex bg-[#F7F6F2] p-1 rounded-xl border border-[#E7E9E4]">
                <button
                  type="button"
                  onClick={() => { setMode("login"); setErrorMsg(""); setSuccessMsg(""); }}
                  className={`flex-1 py-2 rounded-lg font-extrabold text-xs transition-all ${
                    mode === "login" ? "bg-[#287C73] text-white shadow-sm" : "text-[#4B6363]"
                  }`}
                >
                  🔑 Sign In
                </button>

                <button
                  type="button"
                  onClick={() => { setMode("signup"); setErrorMsg(""); setSuccessMsg(""); }}
                  className={`flex-1 py-2 rounded-lg font-extrabold text-xs transition-all ${
                    mode === "signup" ? "bg-[#287C73] text-white shadow-sm" : "text-[#4B6363]"
                  }`}
                >
                  📝 Create Account
                </button>
              </div>

              {/* Alert Banners */}
              {errorMsg && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs font-bold text-red-700">
                  ⚠️ {errorMsg}
                </div>
              )}

              {successMsg && (
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-700 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>{successMsg}</span>
                </div>
              )}

              {mode === "login" ? (
                <form onSubmit={handleLoginSubmit} className="space-y-3.5">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-[#102C2B] block">Email Address</label>
                    <div className="relative">
                      <Mail className="w-4 h-4 text-[#4B6363] absolute left-3 top-2.5" />
                      <input
                        type="email"
                        required
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        placeholder="citizen@civiclens.org"
                        className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-xl pl-9 pr-3 py-2 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-[#102C2B] block">Password</label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-[#4B6363] absolute left-3 top-2.5" />
                      <input
                        type="password"
                        required
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-xl pl-9 pr-3 py-2 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3.5 rounded-xl bg-[#287C73] hover:bg-[#1F645D] text-white font-black text-xs shadow-md flex items-center justify-center gap-2 transition-all hover:scale-[1.01] teal-glow"
                  >
                    {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <>Sign In &amp; Unlock City Dashboard &rarr;</>}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleSignupSubmit} className="space-y-3.5">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-[#102C2B] block">Full Name</label>
                    <div className="relative">
                      <User className="w-4 h-4 text-[#4B6363] absolute left-3 top-2.5" />
                      <input
                        type="text"
                        required
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="Alex Morgan"
                        className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-xl pl-9 pr-3 py-2 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-[#102C2B] block">Email Address</label>
                    <div className="relative">
                      <Mail className="w-4 h-4 text-[#4B6363] absolute left-3 top-2.5" />
                      <input
                        type="email"
                        required
                        value={signupEmail}
                        onChange={(e) => setSignupEmail(e.target.value)}
                        placeholder="alex@civiclens.org"
                        className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-xl pl-9 pr-3 py-2 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-[#102C2B] block">Password</label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-[#4B6363] absolute left-3 top-2.5" />
                      <input
                        type="password"
                        required
                        value={signupPassword}
                        onChange={(e) => setSignupPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-xl pl-9 pr-3 py-2 text-xs text-[#102C2B] font-semibold focus:outline-none focus:border-[#287C73]"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3.5 rounded-xl bg-[#287C73] hover:bg-[#1F645D] text-white font-black text-xs shadow-md flex items-center justify-center gap-2 transition-all hover:scale-[1.01] teal-glow"
                  >
                    {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <>Create Account &amp; Unlock &rarr;</>}
                  </button>
                </form>
              )}
            </div>
          </div>
        </section>
      </div>
    );
  }

  // 2. UNLOCKED MAIN CITY DASHBOARD (DISPLAYED AFTER SIGNIN / ENTRY)
  return (
    <div className="space-y-16 pb-16 animate-fade-in">
      {/* Authenticated User Status Bar */}
      <section className="bg-white border border-[#E7E9E4] rounded-3xl p-8 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <span className="text-xs font-black text-[#10B981] uppercase tracking-wider bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> AUTHENTICATED SESSION ACTIVE
              </span>
              <span className="text-xs font-bold text-[#4B6363]">
                User: <strong>{userProfile?.full_name || "Alex Morgan"}</strong> ({userProfile?.role || "Citizen"})
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-[#102C2B]">
              CivicLens City Intelligence Dashboard
            </h1>
            <p className="text-sm text-[#4B6363] font-medium max-w-xl">
              Report urban grievances, discover active ward incidents on the GIS map, and verify officer resolution evidence.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSignOut}
              className="px-4 py-3 rounded-2xl bg-red-50 hover:bg-red-100 text-red-700 font-extrabold text-xs border border-red-200 flex items-center gap-1.5 transition-colors"
            >
              <LogOut className="w-4 h-4" /> Lock / Sign Out
            </button>

            <Link
              href="/report"
              className="px-6 py-3.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-md flex items-center gap-2 transition-all teal-glow"
            >
              <Camera className="w-4 h-4" /> 📸 Report Issue Now
            </Link>
          </div>
        </div>
      </section>

      {/* Live GIS Map Visualizer Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-black text-[#287C73] uppercase tracking-wider">REAL-TIME SPATIAL DISPATCH</span>
            <h2 className="text-2xl font-black text-[#102C2B]">Central District GIS Map View</h2>
          </div>
          <Link href="/map" className="text-xs font-extrabold text-[#287C73] hover:underline flex items-center gap-1">
            Open Fullscreen GIS Map &rarr;
          </Link>
        </div>

        <MapVisualizer height="h-[540px]" showHeatmapToggle={true} />
      </section>

      {/* Main Flow Navigation Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/report" className="p-6 rounded-3xl bg-white border border-[#E7E9E4] hover:border-[#287C73] transition-all space-y-4 group hover-lift shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-bold text-xl group-hover:scale-110 transition-transform">
            📸
          </div>
          <h3 className="text-lg font-black text-[#102C2B]">1. Report Grievance</h3>
          <p className="text-xs text-[#4B6363] font-medium">Capture photo, Marathi/Hindi/English voice, or video with automatic GPS location logging.</p>
          <span className="text-xs font-extrabold text-[#287C73] block pt-2">Start Report &rarr;</span>
        </Link>

        <Link href="/officer" className="p-6 rounded-3xl bg-white border border-[#E7E9E4] hover:border-[#287C73] transition-all space-y-4 group hover-lift shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-bold text-xl group-hover:scale-110 transition-transform">
            🛡️
          </div>
          <h3 className="text-lg font-black text-[#102C2B]">2. AI Resolution Audit</h3>
          <p className="text-xs text-[#4B6363] font-medium">Side-by-side BEFORE/AFTER visual evidence inspection and multi-factor fake resolution detection.</p>
          <span className="text-xs font-extrabold text-[#287C73] block pt-2">Open Officer Inspector &rarr;</span>
        </Link>

        <Link href="/impact" className="p-6 rounded-3xl bg-white border border-[#E7E9E4] hover:border-[#287C73] transition-all space-y-4 group hover-lift shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-bold text-xl group-hover:scale-110 transition-transform">
            🏆
          </div>
          <h3 className="text-lg font-black text-[#102C2B]">3. Impact &amp; Karma Rewards</h3>
          <p className="text-xs text-[#4B6363] font-medium">Earn Karma Points, unlock badges, view Ward leaderboards, and redeem municipal tax rebates.</p>
          <span className="text-xs font-extrabold text-[#287C73] block pt-2">View Karma Profile &rarr;</span>
        </Link>
      </section>
    </div>
  );
}
