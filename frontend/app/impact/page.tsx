"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { CheckCircle2, ShieldCheck, Award, TrendingUp, Users, Trophy, Ticket, Gift, Sparkles, Star } from "lucide-react";
import CivicCertificate from "@/components/CivicCertificate";

export default function ImpactPage() {
  const [activeTab, setActiveTab] = useState<"overview" | "leaderboard" | "rewards" | "certificate">("overview");
  const [redeemedVoucher, setRedeemedVoucher] = useState<string | null>(null);
  const [userProfile, setUserProfile] = useState<any>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("civiclens_user");
    if (storedUser) {
      try {
        setUserProfile(JSON.parse(storedUser));
      } catch (err) {
        console.error("Invalid session JSON");
      }
    }
  }, []);

  const activeName = userProfile?.full_name || "Alex Morgan";

  const leaderboard = [
    { rank: 1, name: "Ward Champion #63", ward: "Ward 63", karma: 6200, reports: 34, badge: "👑 Ward Champion" },
    { rank: 2, name: "Star Guardian #12", ward: "Ward 12", karma: 5400, reports: 29, badge: "⭐ Star Guardian" },
    { rank: 3, name: `${activeName} (You)`, ward: "Ward 63", karma: 4850, reports: 24, badge: "🛡️ Master Guardian" },
    { rank: 4, name: "Civic Veteran #45", ward: "Ward 45", karma: 4100, reports: 19, badge: "🏅 Civic Veteran" },
    { rank: 5, name: "Active Citizen #18", ward: "Ward 18", karma: 3750, reports: 16, badge: "🌱 Active Citizen" }
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-10 pb-16 animate-fade-in text-[#102C2B]">
      {/* Header */}
      <div className="text-center space-y-3">
        <span className="text-xs font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3.5 py-1 rounded-full border border-[#287C73]/20">
          🏆 Feature 01: Gamified Citizen Impact &amp; Rewards
        </span>
        <h1 className="text-4xl font-black text-[#102C2B]">Civic Impact &amp; Karma Rewards</h1>
        <p className="text-sm text-[#4B6363] font-medium max-w-2xl mx-auto">
          Earn Civic Karma points for filing non-duplicate reports, verifying repair quality, and redeem municipal tax rebates.
        </p>
      </div>

      {/* Tab Switcher */}
      <div className="flex bg-[#F7F6F2] p-1.5 rounded-2xl border border-[#E7E9E4] max-w-xl mx-auto text-xs font-extrabold">
        <button
          type="button"
          onClick={() => setActiveTab("overview")}
          className={`flex-1 py-2.5 rounded-xl transition-all ${
            activeTab === "overview" ? "bg-[#287C73] text-white shadow-sm" : "text-[#4B6363]"
          }`}
        >
          📊 Impact Stats
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("leaderboard")}
          className={`flex-1 py-2.5 rounded-xl transition-all ${
            activeTab === "leaderboard" ? "bg-[#287C73] text-white shadow-sm" : "text-[#4B6363]"
          }`}
        >
          🏆 Leaderboard
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("rewards")}
          className={`flex-1 py-2.5 rounded-xl transition-all ${
            activeTab === "rewards" ? "bg-[#287C73] text-white shadow-sm" : "text-[#4B6363]"
          }`}
        >
          🎁 Karma Rewards
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("certificate")}
          className={`flex-1 py-2.5 rounded-xl transition-all ${
            activeTab === "certificate" ? "bg-[#287C73] text-white shadow-sm" : "text-[#4B6363]"
          }`}
        >
          📜 Certificate
        </button>
      </div>

      {activeTab === "overview" && (
        <div className="space-y-8">
          {/* User Karma Banner */}
          <div className="bg-[#287C73] text-white p-8 rounded-3xl shadow-xl flex flex-col md:flex-row items-center justify-between gap-6 teal-glow">
            <div className="space-y-2 text-center md:text-left">
              <span className="text-xs font-black uppercase tracking-wider opacity-80">YOUR CIVIC PROFILE</span>
              <h2 className="text-3xl font-black">{activeName} — Level 5 Guardian</h2>
              <p className="text-xs opacity-90 font-medium">Ranked #3 in Ward 63 • 24 Verified Grievances Logged</p>
            </div>

            <div className="bg-white/10 backdrop-blur-md border border-white/20 px-6 py-4 rounded-2xl text-center">
              <span className="text-[10px] font-black uppercase tracking-widest text-white/80">TOTAL CIVIC KARMA</span>
              <div className="text-4xl font-black text-white">4,850 <span className="text-xs font-normal">PTS</span></div>
            </div>
          </div>

          {/* Key Impact KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-2 shadow-sm">
              <span className="text-xs font-bold text-[#4B6363]">Total Reports</span>
              <div className="text-4xl font-black text-[#102C2B]">12,482</div>
              <div className="text-xs text-[#287C73] font-bold">100% Geo-verified</div>
            </div>

            <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-2 shadow-sm">
              <span className="text-xs font-bold text-[#4B6363]">Verified Resolved</span>
              <div className="text-4xl font-black text-[#10B981]">9,821</div>
              <div className="text-xs text-[#10B981] font-bold">AI Vision Verified</div>
            </div>

            <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-2 shadow-sm">
              <span className="text-xs font-bold text-[#4B6363]">Average SLA</span>
              <div className="text-4xl font-black text-[#287C73]">2.4 Days</div>
              <div className="text-xs text-[#287C73] font-bold">Down from 14 days</div>
            </div>

            <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-2 shadow-sm">
              <span className="text-xs font-bold text-[#4B6363]">Citizens Impacted</span>
              <div className="text-4xl font-black text-[#102C2B]">142,000+</div>
              <div className="text-xs text-[#10B981] font-bold">Across 4 Wards</div>
            </div>
          </div>

          {/* Unlocked Badges */}
          <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-black text-[#102C2B]">Unlocked Civic Badges</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl bg-[#F7F6F2] border border-[#E7E9E4] flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-[#287C73]/10 text-2xl flex items-center justify-center">🛡️</div>
                <div>
                  <h4 className="font-extrabold text-xs text-[#102C2B]">Urban Guardian</h4>
                  <p className="text-[10px] text-[#4B6363]">Filed 20+ verified reports</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-[#F7F6F2] border border-[#E7E9E4] flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-[#10B981]/10 text-2xl flex items-center justify-center">♻️</div>
                <div>
                  <h4 className="font-extrabold text-xs text-[#102C2B]">Zero Waste Pioneer</h4>
                  <p className="text-[10px] text-[#4B6363]">Flagged 15 waste dumps</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-[#F7F6F2] border border-[#E7E9E4] flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-[#F3B83F]/10 text-2xl flex items-center justify-center">👁️</div>
                <div>
                  <h4 className="font-extrabold text-xs text-[#102C2B]">Resolution Verifier</h4>
                  <p className="text-[10px] text-[#4B6363]">Verified 10 repair photos</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "leaderboard" && (
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-md space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-black text-[#102C2B]">Ward 63 &amp; City Citizen Leaderboard</h3>
            <span className="text-xs font-bold text-[#287C73] bg-[#287C73]/10 px-3 py-1 rounded-full">Updated Live</span>
          </div>

          <div className="space-y-3">
            {leaderboard.map((item) => (
              <div
                key={item.rank}
                className={`p-4 rounded-2xl border flex items-center justify-between ${
                  item.rank === 3
                    ? "bg-[#287C73]/10 border-[#287C73]"
                    : "bg-[#F7F6F2] border-[#E7E9E4]"
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-8 h-8 rounded-full bg-[#102C2B] text-white flex items-center justify-center font-black text-xs">
                    #{item.rank}
                  </div>
                  <div>
                    <h4 className="font-extrabold text-sm text-[#102C2B]">{item.name}</h4>
                    <span className="text-xs text-[#4B6363]">{item.ward} • {item.reports} Reports</span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs font-extrabold text-[#287C73] block">{item.badge}</span>
                  <strong className="text-sm font-black text-[#102C2B]">{item.karma} PTS</strong>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "rewards" && (
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-md space-y-6">
          <h3 className="text-xl font-black text-[#102C2B]">Redeemable Municipal Vouchers</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl border border-[#287C73]/30 bg-[#F7F6F2] space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black text-[#287C73] uppercase">MUNICIPAL PARKING</span>
                <span className="text-xs font-bold bg-[#10B981]/10 text-[#10B981] px-2.5 py-0.5 rounded-full">AVAILABLE</span>
              </div>
              <h4 className="text-lg font-black text-[#102C2B]">₹200 Parking Credit Voucher</h4>
              <p className="text-xs text-[#4B6363]">Redeemable at all municipal smart parking lots across Central District.</p>
              <button
                type="button"
                onClick={() => setRedeemedVoucher("CIVIC-PARK-2026-X89")}
                className="w-full py-2.5 rounded-xl bg-[#287C73] text-white font-extrabold text-xs"
              >
                {redeemedVoucher === "CIVIC-PARK-2026-X89" ? "Code: CIVIC-PARK-2026-X89 ✓" : "Redeem (1,500 Karma PTS)"}
              </button>
            </div>

            <div className="p-6 rounded-2xl border border-[#287C73]/30 bg-[#F7F6F2] space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black text-[#287C73] uppercase">PROPERTY TAX REBATE</span>
                <span className="text-xs font-bold bg-[#10B981]/10 text-[#10B981] px-2.5 py-0.5 rounded-full">AVAILABLE</span>
              </div>
              <h4 className="text-lg font-black text-[#102C2B]">5% Property Tax Rebate</h4>
              <p className="text-xs text-[#4B6363]">Apply 5% rebate voucher on annual municipal property tax bill.</p>
              <button
                type="button"
                onClick={() => setRedeemedVoucher("CIVIC-TAX-5PCT-99")}
                className="w-full py-2.5 rounded-xl bg-[#287C73] text-white font-extrabold text-xs"
              >
                {redeemedVoucher === "CIVIC-TAX-5PCT-99" ? "Code: CIVIC-TAX-5PCT-99 ✓" : "Redeem (3,000 Karma PTS)"}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === "certificate" && (
        <div className="space-y-4">
          <CivicCertificate userName={activeName} karmaPoints={4850} ward="Ward 63 (College Road)" />
        </div>
      )}
    </div>
  );
}
