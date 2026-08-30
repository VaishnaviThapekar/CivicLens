"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  MapPin, Search, Sparkles, AlertTriangle, CheckCircle2, Clock,
  ArrowRight, Activity, Flame, ShieldAlert, ChevronRight, Eye, RefreshCw,
  Vote, Award, Check
} from "lucide-react";
import MapVisualizer from "@/components/MapVisualizer";

const SPATIAL_HOTSPOTS = [
  {
    id: "p1",
    title: "Arterial Road Infrastructure Hotspot",
    category: "Roads",
    icon: "🛣️",
    ward: "Central District — Sector 4",
    priority: "P1 — Critical",
    ai_score: 91,
    reports_count: 14,
    status: "Repair in progress",
    nearby: ["🚌 Bus stop", "🏫 City Campus", "🚦 Major intersection"],
    desc: "Severe road crater causing morning traffic bottleneck. High safety risk due to pedestrian traffic.",
    x: 38,
    y: 32
  },
  {
    id: "p2",
    title: "Stormwater Underpass Drain Line",
    category: "Water",
    icon: "💧",
    ward: "South District — Sector 12",
    priority: "P1 — Critical",
    ai_score: 88,
    reports_count: 28,
    status: "AI Clustered",
    nearby: ["🛍️ Market Road", "🌊 River Corridor Line"],
    desc: "Clogged drainage line causing flash waterlogging across 400m street corridor.",
    x: 62,
    y: 55
  },
  {
    id: "p3",
    title: "Campus Overflowing Sanitation Bin",
    category: "Waste",
    icon: "🗑️",
    ward: "North District — Sector 45",
    priority: "P2 — High",
    ai_score: 74,
    reports_count: 8,
    status: "Verified Resolved",
    nearby: ["🌳 Public Park", "🏫 Primary School"],
    desc: "Overflowing waste bin cleared and disinfected by Municipal Sanitation team.",
    x: 22,
    y: 38
  }
];

export default function PublicCityExploration() {
  const [activeCategory, setActiveCategory] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedIssue, setSelectedIssue] = useState<any>(SPATIAL_HOTSPOTS[0]);
  const [proposals, setProposals] = useState<any[]>([]);
  const [votedProposalId, setVotedProposalId] = useState<string | null>(null);

  useEffect(() => {
    fetchProposals();
  }, []);

  const fetchProposals = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/intelligence/governance/proposals");
      if (res.ok) {
        setProposals(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleVote = async (propId: string) => {
    try {
      const res = await fetch("http://localhost:8000/api/intelligence/governance/proposals/vote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ proposal_id: propId, karma_pts: 50 })
      });
      if (res.ok) {
        setVotedProposalId(propId);
        await fetchProposals();
      }
    } catch (err) {
      alert("Vote error");
    }
  };

  const filteredHotspots = SPATIAL_HOTSPOTS.filter(h => {
    const catMatch = activeCategory === "ALL" || h.category.toUpperCase() === activeCategory.toUpperCase();
    const searchMatch = !searchQuery || h.title.toLowerCase().includes(searchQuery.toLowerCase()) || h.ward.toLowerCase().includes(searchQuery.toLowerCase());
    return catMatch && searchMatch;
  });

  return (
    <div className="space-y-16 pb-16 animate-fade-in">
      {/* 1. HERO TITLE & SEARCH */}
      <section className="text-center max-w-3xl mx-auto space-y-4 pt-4">
        <span className="text-xs font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3.5 py-1 rounded-full border border-[#287C73]/20">
          📍 Live City Intelligence Grid
        </span>
        <h1 className="text-4xl sm:text-5xl font-black text-[#102C2B] tracking-tight">
          WHAT'S HAPPENING IN YOUR CITY?
        </h1>
        <p className="text-base text-[#4B6363] font-medium max-w-xl mx-auto">
          Explore civic issues, emerging hotspots, and participate in ward budget voting across the city.
        </p>

        {/* Large Search Bar */}
        <div className="max-w-xl mx-auto relative pt-2">
          <Search className="w-5 h-5 text-[#4B6363] absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search a neighbourhood, road or landmark..."
            className="w-full bg-white border border-[#E7E9E4] rounded-2xl pl-12 pr-4 py-4 text-sm text-[#102C2B] focus:outline-none focus:border-[#287C73] font-semibold shadow-sm"
          />
        </div>
      </section>

      {/* 2. HERO VECTOR MAP & ISSUE DRAWER */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Full Viewport Interactive Map */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-white border border-[#E7E9E4] rounded-3xl p-4 shadow-sm relative overflow-hidden space-y-3">
            {/* Map Header Filter Pills */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-[#E7E9E4]">
              <button
                onClick={() => setActiveCategory("ALL")}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold transition-all shrink-0 ${
                  activeCategory === "ALL" ? "bg-[#287C73] text-white shadow-sm" : "bg-[#F7F6F2] text-[#4B6363] border border-[#E7E9E4]"
                }`}
              >
                All Issues (184)
              </button>
              <button
                onClick={() => setActiveCategory("ROADS")}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold transition-all shrink-0 ${
                  activeCategory === "ROADS" ? "bg-[#287C73] text-white shadow-sm" : "bg-[#F7F6F2] text-[#4B6363] border border-[#E7E9E4]"
                }`}
              >
                🛣️ Roads (72)
              </button>
              <button
                onClick={() => setActiveCategory("WATER")}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold transition-all shrink-0 ${
                  activeCategory === "WATER" ? "bg-[#287C73] text-white shadow-sm" : "bg-[#F7F6F2] text-[#4B6363] border border-[#E7E9E4]"
                }`}
              >
                💧 Water (41)
              </button>
              <button
                onClick={() => setActiveCategory("WASTE")}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold transition-all shrink-0 ${
                  activeCategory === "WASTE" ? "bg-[#287C73] text-white shadow-sm" : "bg-[#F7F6F2] text-[#4B6363] border border-[#E7E9E4]"
                }`}
              >
                🗑️ Waste (32)
              </button>
            </div>

            {/* Vector Map Component */}
            <MapVisualizer
              height="h-[460px]"
              theme="light"
              pins={filteredHotspots}
              onPinSelect={(pin) => setSelectedIssue(pin)}
              selectedPinId={selectedIssue?.id}
            />
          </div>
        </div>

        {/* Product-Style Issue Detail Drawer */}
        <div className="lg:col-span-4 bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-md space-y-6">
          {selectedIssue ? (
            <div className="space-y-5">
              <div className="flex items-center justify-between border-b border-[#E7E9E4] pb-3">
                <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#287C73]/10 text-[#287C73]">
                  {selectedIssue.icon} {selectedIssue.category}
                </span>
                <span className="text-xs font-extrabold text-[#D94F4F] bg-[#D94F4F]/10 px-2.5 py-0.5 rounded">
                  {selectedIssue.priority}
                </span>
              </div>

              <div className="space-y-1">
                <h2 className="text-xl font-black text-[#102C2B]">{selectedIssue.title}</h2>
                <p className="text-xs font-bold text-[#4B6363]">{selectedIssue.ward}</p>
              </div>

              {/* AI Assessment Card */}
              <div className="p-4 bg-[#F7F6F2] rounded-2xl border border-[#E7E9E4] space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold text-[#287C73] flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" /> AI Assessment
                  </span>
                  <span className="text-sm font-black text-[#D94F4F]">{selectedIssue.ai_score} / 100</span>
                </div>
                <p className="text-xs text-[#102C2B] font-medium leading-relaxed">{selectedIssue.desc}</p>
              </div>

              {/* Supporting Citizens */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-extrabold text-[#102C2B]">{selectedIssue.reports_count} citizens reported this</span>
                  <span className="text-[#287C73] font-bold">1 Incident</span>
                </div>

                <div className="flex items-center space-x-1">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="w-6 h-6 rounded-full bg-[#287C73] text-white flex items-center justify-center text-[10px] font-black border-2 border-white">
                      👤
                    </div>
                  ))}
                  <span className="text-xs font-bold text-[#4B6363] pl-1">+{selectedIssue.reports_count - 6} more</span>
                </div>
              </div>

              <Link
                href="/report"
                className="w-full py-3.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-lg flex items-center justify-center gap-2 transition-all teal-glow"
              >
                + Add Supporting Report
              </Link>
            </div>
          ) : (
            <div className="text-center py-20 text-[#4B6363] text-xs">Select an issue on the map</div>
          )}
        </div>
      </section>

      {/* 3. PARTICIPATORY WARD BUDGETING & TOWNHALL VOTING */}
      <section className="bg-white border border-[#E7E9E4] rounded-3xl p-8 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-[#E7E9E4] pb-4">
          <div>
            <span className="text-xs font-black text-[#287C73] uppercase tracking-wider flex items-center gap-2">
              <Vote className="w-4 h-4 text-[#287C73]" /> Participatory Ward Budgeting &amp; Townhall Voting
            </span>
            <h2 className="text-2xl font-black text-[#102C2B]">Vote on Municipal Infrastructure Proposals</h2>
          </div>
          <span className="text-xs text-[#4B6363] font-bold">Allocate Civic Karma (50 PTS / Vote)</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {proposals.map((prop) => (
            <div key={prop.id} className="p-5 rounded-2xl bg-[#F7F6F2] border border-[#E7E9E4] space-y-4 hover-lift">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-black text-[#287C73] uppercase bg-white px-2.5 py-0.5 rounded border border-[#E7E9E4]">
                  {prop.category}
                </span>
                <span className="text-[10px] font-bold bg-[#10B981]/10 text-[#10B981] px-2 py-0.5 rounded-full">
                  {prop.status}
                </span>
              </div>

              <h3 className="font-extrabold text-sm text-[#102C2B] leading-snug">{prop.title}</h3>
              <p className="text-xs text-[#4B6363] leading-relaxed">{prop.description}</p>

              <div className="pt-2 border-t border-[#E7E9E4] flex items-center justify-between text-xs">
                <div>
                  <span className="text-[#4B6363] text-[10px] block">Est. Budget:</span>
                  <strong className="text-[#102C2B] font-extrabold">{prop.estimated_budget_inr}</strong>
                </div>

                <div className="text-right">
                  <span className="text-[#287C73] font-bold block">{prop.votes_count} Votes</span>
                  <span className="text-[10px] text-[#4B6363] font-mono">{prop.karma_points_allocated} PTS</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => handleVote(prop.id)}
                className={`w-full py-2.5 rounded-xl font-extrabold text-xs flex items-center justify-center gap-1.5 transition-all ${
                  votedProposalId === prop.id
                    ? "bg-[#10B981] text-white"
                    : "bg-[#287C73] hover:bg-[#1F645D] text-white teal-glow shadow-md"
                }`}
              >
                {votedProposalId === prop.id ? <><Check className="w-4 h-4" /> Voted (50 Karma PTS Allocated)</> : <>Vote with 50 Karma PTS &rarr;</>}
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
