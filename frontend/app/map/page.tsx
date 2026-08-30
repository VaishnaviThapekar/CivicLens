"use client";

import { useState } from "react";
import MapVisualizer from "@/components/MapVisualizer";
import { Flame, ShieldAlert, CheckCircle2, TrendingUp, Cpu, Users, Sparkles } from "lucide-react";

export default function CityMapPage() {
  const [selectedIssueDetail, setSelectedIssueDetail] = useState<any | null>(null);

  return (
    <div className="space-y-8 pb-16 animate-fade-in">
      {/* Header Title */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3.5 py-1 rounded-full border border-[#287C73]/20">
            Live City GIS Spatial Intelligence
          </span>
          <h1 className="text-3xl font-black text-[#102C2B] mt-2">Interactive City Map &amp; Hotspots</h1>
          <p className="text-xs text-[#4B6363] font-medium mt-1">
            Real-time PostGIS spatial mapping of active issues, resolved fixes, civic hotspots, and emerging infrastructure risks.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-white border border-[#E7E9E4] px-3 py-2 rounded-2xl text-center shadow-sm">
            <span className="block text-[10px] text-[#4B6363] font-bold">Active Hotspots</span>
            <span className="text-sm font-black text-[#D94F4F]">4 Hotspots</span>
          </div>

          <div className="bg-white border border-[#E7E9E4] px-3 py-2 rounded-2xl text-center shadow-sm">
            <span className="block text-[10px] text-[#4B6363] font-bold">Resolution Rate</span>
            <span className="text-sm font-black text-[#287C73]">96% AI Verified</span>
          </div>
        </div>
      </div>

      {/* Main Interactive Map Component */}
      <MapVisualizer showHeatmapToggle={true} onSelectIssue={(issue) => setSelectedIssueDetail(issue)} />

      {/* Civic Hotspots & Emerging Risk Clusters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 space-y-3 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-2xl bg-[#D94F4F]/10 text-[#D94F4F] flex items-center justify-center font-bold">
              <Flame className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-black uppercase tracking-wider bg-red-100 text-red-700 px-2.5 py-1 rounded-full">
              Hotspot #1
            </span>
          </div>
          <h3 className="text-base font-extrabold text-[#102C2B]">College Road Corridor</h3>
          <p className="text-xs text-[#4B6363] font-medium">
            High concentration of asphalt sub-base erosion &amp; recurring potholes due to underground pipe seepage.
          </p>
          <div className="pt-2 border-t border-[#E7E9E4] flex justify-between text-xs font-bold">
            <span className="text-[#4B6363]">Supporting Reports:</span>
            <span className="text-[#D94F4F]">38 Citizens</span>
          </div>
        </div>

        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 space-y-3 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-2xl bg-[#F3B83F]/10 text-[#F3B83F] flex items-center justify-center font-bold">
              <TrendingUp className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-black uppercase tracking-wider bg-amber-100 text-amber-700 px-2.5 py-1 rounded-full">
              Emerging Issue
            </span>
          </div>
          <h3 className="text-base font-extrabold text-[#102C2B]">Market Street Sector 4</h3>
          <p className="text-xs text-[#4B6363] font-medium">
            Commercial waste dumping accumulation spike observed during peak weekend markets.
          </p>
          <div className="pt-2 border-t border-[#E7E9E4] flex justify-between text-xs font-bold">
            <span className="text-[#4B6363]">Supporting Reports:</span>
            <span className="text-[#F3B83F]">24 Citizens</span>
          </div>
        </div>

        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 space-y-3 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-2xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-bold">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-black uppercase tracking-wider bg-[#287C73]/10 text-[#287C73] px-2.5 py-1 rounded-full">
              AI Cluster Notice
            </span>
          </div>
          <h3 className="text-base font-extrabold text-[#102C2B]">Indira Nagar Underpass</h3>
          <p className="text-xs text-[#4B6363] font-medium">
            Stormwater drain silt clogging causing 4.5m² waterlogging during monsoon downpours.
          </p>
          <div className="pt-2 border-t border-[#E7E9E4] flex justify-between text-xs font-bold">
            <span className="text-[#4B6363]">Supporting Reports:</span>
            <span className="text-[#287C73]">52 Citizens</span>
          </div>
        </div>
      </div>
    </div>
  );
}
