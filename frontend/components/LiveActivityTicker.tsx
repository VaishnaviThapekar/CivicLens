"use client";

import { useEffect, useState } from "react";
import { Sparkles, Award, CheckCircle2, ShieldCheck } from "lucide-react";

const TICKER_ITEMS = [
  "✨ Ward 63 Pothole #CL-2026-0049 AI Verified Resolved",
  "🏆 Alex Morgan earned 1,500 Civic Karma PTS & claimed ₹200 Parking Rebate",
  "🚛 4.2 Tons Cold Mix Asphalt dispatched to PWD Depot #4 for Ward 12 patch work",
  "💧 Market Street Pipe Leak anomaly detected by Drone Infrared • Isolated within 18h ETA",
  "🗳️ Ward 63 Solar Streetlight proposal reached 518 votes on Townhall Portal"
];

export default function LiveActivityTicker() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % TICKER_ITEMS.length);
    }, 4500);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="bg-[#102C2B] text-white py-2 px-4 text-xs font-bold flex items-center justify-between border-b border-[#287C73]/40 shadow-inner">
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
        <div className="flex items-center gap-2 overflow-hidden">
          <span className="text-[10px] font-black uppercase tracking-wider text-[#F3B83F] bg-[#F3B83F]/15 px-2.5 py-0.5 rounded-full border border-[#F3B83F]/30 flex items-center gap-1 shrink-0">
            <Sparkles className="w-3 h-3 text-[#F3B83F]" /> LIVE CIVIC STREAM
          </span>
          <p className="text-gray-200 truncate animate-fade-in font-medium text-xs">
            {TICKER_ITEMS[index]}
          </p>
        </div>

        <div className="hidden md:flex items-center gap-4 text-[11px] text-gray-300 shrink-0">
          <span className="flex items-center gap-1 text-emerald-400 font-extrabold">
            <CheckCircle2 className="w-3.5 h-3.5" /> 100% SLA Enforced
          </span>
          <span>☎️ Municipal Desk: <strong>1800-22-CIVIC</strong></span>
        </div>
      </div>
    </div>
  );
}
