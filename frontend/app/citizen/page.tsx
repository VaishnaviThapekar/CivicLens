"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Award, CheckCircle2, Clock, Camera, AlertTriangle, Eye, Sparkles,
  UserCheck, ShieldCheck, ArrowRight, RefreshCw, Inbox, MapPin,
  Bell, Globe, Phone, Mail, User, Shield, Lock
} from "lucide-react";
import { fetchComplaints } from "@/lib/api";

export default function CitizenProfileDashboard() {
  const [userSession, setUserSession] = useState<any>(null);
  const [complaints, setComplaints] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"profile" | "reports" | "notifications" | "history">("profile");

  useEffect(() => {
    const storedUser = localStorage.getItem("civiclens_user");
    if (storedUser) {
      try {
        setUserSession(JSON.parse(storedUser));
      } catch (err) {
        console.error("Invalid session JSON");
      }
    }
    loadComplaints();
  }, []);

  const loadComplaints = async () => {
    setLoading(true);
    try {
      const c = await fetchComplaints();
      setComplaints(c);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // If no active logged in user session, show clean Auth Guard Prompt
  if (!userSession) {
    return (
      <div className="max-w-md mx-auto my-12 bg-white border border-[#E7E9E4] rounded-3xl p-8 shadow-xl text-center space-y-5 animate-fade-in">
        <div className="w-14 h-14 rounded-2xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-black text-2xl mx-auto border border-[#287C73]/20">
          <Lock className="w-6 h-6 text-[#287C73]" />
        </div>
        <div className="space-y-1">
          <h2 className="text-xl font-black text-[#102C2B]">No Active User Session</h2>
          <p className="text-xs text-[#4B6363] font-semibold">
            Please sign in or create an account to view your citizen profile, contribution karma, and submitted reports.
          </p>
        </div>

        <Link
          href="/"
          className="w-full py-3.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-md flex items-center justify-center gap-2 transition-all teal-glow"
        >
          🔑 Sign In / Create Account &rarr;
        </Link>
      </div>
    );
  }

  const p = userSession;

  return (
    <div className="space-y-8 pb-12 animate-fade-in">
      {/* Dynamic Citizen Profile Header */}
      <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 sm:p-8 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 hover-lift">
        <div className="flex items-center space-x-5">
          <div className="w-20 h-20 rounded-2xl bg-[#287C73] text-white flex items-center justify-center font-black text-3xl shadow-md overflow-hidden border-2 border-white teal-glow">
            {p.profile_photo_url ? (
              <img src={p.profile_photo_url} alt="Profile" className="w-full h-full object-cover" />
            ) : (
              <span>{p.full_name?.charAt(0) || "U"}</span>
            )}
          </div>
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-extrabold px-3 py-0.5 rounded-full bg-[#287C73]/10 text-[#287C73] border border-[#287C73]/20">
                Verified {p.role || "Citizen"}
              </span>
              <span className="text-xs text-[#4B6363] font-semibold flex items-center gap-1">
                <Globe className="w-3.5 h-3.5 text-[#287C73]" /> {p.preferred_language || "English"}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-[#102C2B]">{p.full_name}</h1>
            <p className="text-xs text-[#4B6363] font-medium flex items-center gap-2">
              <span><Mail className="w-3 h-3 inline mr-1 text-[#287C73]" /> {p.email}</span>
              <span>•</span>
              <span><Phone className="w-3 h-3 inline mr-1 text-[#287C73]" /> {p.phone || "+91 Live Verified"}</span>
            </p>
          </div>
        </div>

        <Link
          href="/report"
          className="px-6 py-3.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-lg shadow-[#287C73]/20 flex items-center gap-2 transition-all teal-glow"
        >
          <Camera className="w-4 h-4" /> 📸 Report New Issue
        </Link>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center space-x-2 border-b border-[#E7E9E4] pb-2 text-xs font-extrabold text-[#4B6363]">
        <button
          onClick={() => setActiveTab("profile")}
          className={`px-4 py-2 rounded-xl transition-all ${
            activeTab === "profile" ? "bg-[#287C73] text-white shadow-sm" : "hover:text-[#102C2B]"
          }`}
        >
          User Profile
        </button>
        <button
          onClick={() => setActiveTab("reports")}
          className={`px-4 py-2 rounded-xl transition-all ${
            activeTab === "reports" ? "bg-[#287C73] text-white shadow-sm" : "hover:text-[#102C2B]"
          }`}
        >
          My Reports ({complaints.length})
        </button>
        <button
          onClick={() => setActiveTab("notifications")}
          className={`px-4 py-2 rounded-xl transition-all ${
            activeTab === "notifications" ? "bg-[#287C73] text-white shadow-sm" : "hover:text-[#102C2B]"
          }`}
        >
          Notifications ({p.notifications?.length || 1})
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`px-4 py-2 rounded-xl transition-all ${
            activeTab === "history" ? "bg-[#287C73] text-white shadow-sm" : "hover:text-[#102C2B]"
          }`}
        >
          Contribution Log
        </button>
      </div>

      {/* Tab 1: Profile Information */}
      {activeTab === "profile" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-4 shadow-sm">
            <h2 className="text-sm font-black text-[#102C2B] uppercase tracking-wider flex items-center gap-2">
              <User className="w-4 h-4 text-[#287C73]" /> Profile Account Details
            </h2>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-[#E7E9E4]">
                <span className="text-[#4B6363]">Full Name:</span>
                <span className="font-extrabold text-[#102C2B]">{p.full_name}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-[#E7E9E4]">
                <span className="text-[#4B6363]">Email Address:</span>
                <span className="font-extrabold text-[#102C2B]">{p.email}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-[#E7E9E4]">
                <span className="text-[#4B6363]">Account Role:</span>
                <span className="font-extrabold text-[#287C73]">{p.role || "Citizen"}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-[#E7E9E4]">
                <span className="text-[#4B6363]">Preferred Language:</span>
                <span className="font-extrabold text-[#287C73]">{p.preferred_language || "English"}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-[#4B6363]">Default Location:</span>
                <span className="font-extrabold text-[#102C2B]">{p.default_location?.city || "Central District"} • {p.default_location?.ward || "Ward 63"}</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-[#287C73] to-[#1F645D] text-white p-6 rounded-3xl space-y-4 shadow-xl teal-glow">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center text-2xl">🏆</div>
              <div>
                <span className="text-xs uppercase font-extrabold opacity-90">Civic Achievement Badge</span>
                <h3 className="text-xl font-black">Active Community Guardian</h3>
              </div>
            </div>
            <p className="text-xs opacity-90 leading-relaxed font-medium">
              Welcome to CivicLens! You can earn Karma Points and Badges by submitting verified reports and confirming resolution evidence in your ward.
            </p>
          </div>
        </div>
      )}

      {/* Tab 2: My Reports */}
      {activeTab === "reports" && (
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-sm space-y-4">
          <h2 className="text-sm font-black text-[#102C2B] uppercase tracking-wider flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#287C73]" /> My Reported Incidents ({complaints.length})
          </h2>

          {complaints.length > 0 ? (
            <div className="space-y-3">
              {complaints.map((c) => (
                <div key={c.id} className="p-4 bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl space-y-2 text-xs hover-lift">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-[#287C73] bg-white px-2.5 py-0.5 rounded border border-[#E7E9E4]">
                      {c.tracking_number}
                    </span>
                    <span className="font-bold text-[#10B981] px-2.5 py-0.5 rounded-full bg-[#10B981]/10">
                      {c.status}
                    </span>
                  </div>
                  <h3 className="font-extrabold text-[#102C2B] text-sm">{c.title}</h3>
                  <p className="text-[#4B6363]">{c.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-[#4B6363] text-xs">No reports submitted yet</div>
          )}
        </div>
      )}

      {/* Tab 3: Notifications */}
      {activeTab === "notifications" && (
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-sm space-y-4">
          <h2 className="text-sm font-black text-[#102C2B] uppercase tracking-wider flex items-center gap-2">
            <Bell className="w-4 h-4 text-[#287C73]" /> Activity Notifications
          </h2>

          <div className="space-y-3">
            <div className="p-4 bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl text-xs space-y-1">
              <div className="flex justify-between items-center">
                <span className="font-extrabold text-[#102C2B]">Welcome to CivicLens</span>
                <span className="text-[10px] text-[#4B6363]">Just now</span>
              </div>
              <p className="text-[#4B6363]">Your user profile is active. You can report urban issues and view live ward resolution progress.</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Contribution Log */}
      {activeTab === "history" && (
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-sm space-y-4">
          <h2 className="text-sm font-black text-[#102C2B] uppercase tracking-wider flex items-center gap-2">
            <Award className="w-4 h-4 text-[#287C73]" /> Contribution History Log
          </h2>

          <div className="space-y-2">
            <div className="p-3 bg-[#F7F6F2] border border-[#E7E9E4] rounded-xl text-xs flex justify-between items-center">
              <span className="font-extrabold text-[#102C2B]">User Account Created &amp; Verified</span>
              <span className="font-mono font-black text-[#10B981]">+50 pts</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
