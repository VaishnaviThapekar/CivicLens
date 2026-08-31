"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Lock, Mail, User, ShieldCheck, ArrowRight, Sparkles, CheckCircle2, RefreshCw, KeyRound, Globe, Compass,
  Camera, MapPin, Eye, Activity, ShieldAlert, Award, LogOut, Building2, Layers, TrendingUp, Zap, Cpu, Award as AwardIcon, CheckCircle
} from "lucide-react";
import MapVisualizer from "@/components/MapVisualizer";
import ARDefectScanner from "@/components/ARDefectScanner";
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
      }, 600);
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
      }, 800);
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

  // LANDING HERO & AUTH GATEWAY FOR UNAUTHENTICATED USERS
  if (!isAuthenticated) {
    return (
      <div className="space-y-16 pb-20 animate-fade-in text-[#102C2B]">
        {/* Executive Hero Section */}
        <section className="relative overflow-hidden bg-white border border-[#E7E9E4] rounded-3xl p-8 sm:p-12 shadow-xl">
          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            {/* Left Column: Platform Value & Live Telemetry */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#287C73]/10 text-[#287C73] border border-[#287C73]/20 text-xs font-black uppercase tracking-wider">
                <Sparkles className="w-4 h-4 text-[#287C73]" /> Next-Gen AI Civic Intelligence &amp; Autonomous Governance
              </div>

              <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-tight text-[#102C2B]">
                See Your City. <br />
                <span className="text-[#287C73]">Make It Better.</span>
              </h1>

              <p className="text-sm sm:text-base text-[#4B6363] font-medium leading-relaxed max-w-xl">
                CivicLens combines 3D AR camera defect scanning, multimodal voice transcription (Marathi, Hindi, English), spatial DBSCAN clustering, and autonomous Agentic AI dispatching to transform urban reports into verified civic action.
              </p>

              {/* Key Platform KPI Badges */}
              <div className="grid grid-cols-3 gap-4 pt-2">
                <div className="bg-[#F7F6F2] border border-[#E7E9E4] p-4 rounded-2xl">
                  <span className="text-[10px] uppercase font-black text-[#4B6363] block">RESOLVED INCIDENTS</span>
                  <strong className="text-xl sm:text-2xl font-black text-[#287C73]">12,482</strong>
                </div>

                <div className="bg-[#F7F6F2] border border-[#E7E9E4] p-4 rounded-2xl">
                  <span className="text-[10px] uppercase font-black text-[#4B6363] block">AI VISION ACCURACY</span>
                  <strong className="text-xl sm:text-2xl font-black text-[#10B981]">98.4%</strong>
                </div>

                <div className="bg-[#F7F6F2] border border-[#E7E9E4] p-4 rounded-2xl">
                  <span className="text-[10px] uppercase font-black text-[#4B6363] block">AVERAGE SLA</span>
                  <strong className="text-xl sm:text-2xl font-black text-[#102C2B]">2.4 Hours</strong>
                </div>
              </div>
            </div>

            {/* Right Column: High-End Sign In Gate Card */}
            <div className="lg:col-span-5 bg-white border border-[#E7E9E4] rounded-3xl p-8 shadow-2xl space-y-5 relative">
              <div className="text-center space-y-1">
                <span className="text-[10px] font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3 py-0.5 rounded-full border border-[#287C73]/20">
                  🔐 AUTHENTICATION GATEWAY
                </span>
                <h2 className="text-2xl font-black text-[#102C2B]">Sign In to City Dashboard</h2>
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
                    {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <>Sign In &amp; Unlock City Platform &rarr;</>}
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

        {/* Feature Highlights Grid */}
        <section className="space-y-6">
          <div className="text-center space-y-2 max-w-2xl mx-auto">
            <span className="text-xs font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3.5 py-1 rounded-full border border-[#287C73]/20">
              ⚡ PLATFORM CAPABILITIES
            </span>
            <h2 className="text-3xl font-black text-[#102C2B]">Engineered for Next-Gen Cities</h2>
            <p className="text-xs text-[#4B6363] font-medium">
              Closing the loop between citizen grievances, municipal field crews, third-party contractors, and municipal leadership.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-3 hover-lift shadow-sm">
              <div className="w-10 h-10 rounded-2xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-bold text-xl">
                📷
              </div>
              <h3 className="font-extrabold text-base text-[#102C2B]">Real-Time 3D AR Camera HUD</h3>
              <p className="text-xs text-[#4B6363] font-medium leading-relaxed">
                Augmented reality camera view estimating defect depth, calculating surface area in m², and capturing GPS coordinates automatically.
              </p>
            </div>

            <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-3 hover-lift shadow-sm">
              <div className="w-10 h-10 rounded-2xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-bold text-xl">
                🤖
              </div>
              <h3 className="font-extrabold text-base text-[#102C2B]">Autonomous Agentic LLM Dispatch</h3>
              <p className="text-xs text-[#4B6363] font-medium leading-relaxed">
                Agentic reasoning loop auto-querying GIS ward databases, estimating required repair materials, and issuing PWD work orders autonomously.
              </p>
            </div>

            <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-3 hover-lift shadow-sm">
              <div className="w-10 h-10 rounded-2xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-bold text-xl">
                🛡️
              </div>
              <h3 className="font-extrabold text-base text-[#102C2B]">Visual Evidence Anti-Fraud Audit</h3>
              <p className="text-xs text-[#4B6363] font-medium leading-relaxed">
                SSIM structural similarity and dHash perceptual fingerprinting comparing BEFORE vs AFTER photos to reject fake or recycled resolution uploads.
              </p>
            </div>
          </div>
        </section>
      </div>
    );
  }

  // UNLOCKED MAIN CITY DASHBOARD FOR AUTHENTICATED USERS
  return (
    <div className="space-y-16 pb-16 animate-fade-in text-[#102C2B]">
      {/* Authenticated User Banner */}
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
