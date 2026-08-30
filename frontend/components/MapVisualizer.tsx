"use client";

import { useState } from "react";
import {
  MapPin, Mail, Phone, ExternalLink, Navigation, ZoomIn, ZoomOut,
  Layers, ThumbsUp, ShieldAlert, CheckCircle2, Clock, Search, Sparkles, Filter, Users
} from "lucide-react";

interface MapVisualizerProps {
  showHeatmapToggle?: boolean;
  onSelectIssue?: (issue: any) => void;
  height?: string;
  theme?: string;
  pins?: any[];
  onPinSelect?: (pin: any) => void;
  selectedPinId?: any;
}

const MOCK_MAP_ISSUES = [
  {
    id: "c-101",
    tracking_number: "CL-NK-2026-00101",
    title: "Deep Pothole Crater on College Road",
    category: "Roads & Bridges",
    subcategory: "Pothole",
    severity: "Critical",
    priority_score: 94,
    status: "In Progress",
    lat: 19.9975,
    lng: 73.7898,
    ward: "Ward 63 — College Road",
    road: "121 College Road Avenue",
    landmark: "Near City Campus Gate 2 & Bus Stop",
    pincode: "422005",
    email: "pwd-roads@civiclens.org",
    phone: "+91 98765 43210 (Eng. R. K. Patil)",
    supporting_count: 38,
    ai_confidence: 96,
    area_m2: 1.85,
    created_at: "2 Hours ago",
    root_cause: "Underground Pipe Leakage Sub-Base Weakening",
    image_url: "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop",
    x: 42,
    y: 38
  },
  {
    id: "c-102",
    tracking_number: "CL-NK-2026-00102",
    title: "Overflowing Commercial Waste Container",
    category: "Sanitation & Waste",
    subcategory: "Overflowing Bin",
    severity: "High",
    priority_score: 78,
    status: "Submitted",
    lat: 20.0050,
    lng: 73.7750,
    ward: "Ward 42 — Market Street",
    road: "45 Market Street Corridor",
    landmark: "Behind Central Vegetable Market",
    pincode: "422001",
    email: "sanitation@civiclens.org",
    phone: "+91 98765 12345 (Officer V. Sharma)",
    supporting_count: 24,
    ai_confidence: 91,
    area_m2: 3.20,
    created_at: "5 Hours ago",
    root_cause: "Uncollected Commercial Waste Accumulation",
    image_url: "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=600&auto=format&fit=crop",
    x: 68,
    y: 28
  },
  {
    id: "c-103",
    tracking_number: "CL-NK-2026-00103",
    title: "Stormwater Drain Overflow & Flooding",
    category: "Drainage & Sewerage",
    subcategory: "Clogged Drain",
    severity: "Critical",
    priority_score: 92,
    status: "Submitted",
    lat: 19.9880,
    lng: 73.7950,
    ward: "Ward 18 — Indira Nagar",
    road: "88 Indira Nagar Link",
    landmark: "Underpass Sector 4",
    pincode: "422009",
    email: "drainage@civiclens.org",
    phone: "+91 98765 67890 (Supervisor S. Deshmukh)",
    supporting_count: 52,
    ai_confidence: 89,
    area_m2: 4.50,
    created_at: "1 Day ago",
    root_cause: "Silt Accumulation in Main Channel",
    image_url: "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600&auto=format&fit=crop",
    x: 30,
    y: 72
  }
];

export default function MapVisualizer({
  showHeatmapToggle = true,
  onSelectIssue,
  pins,
  onPinSelect,
  selectedPinId
}: MapVisualizerProps) {
  const currentIssuesList = pins && pins.length > 0 ? pins : MOCK_MAP_ISSUES;
  const [activeIssue, setActiveIssue] = useState<any>(currentIssuesList[0]);
  const [zoomLevel, setZoomLevel] = useState(120);
  const [mapLayer, setMapLayer] = useState<"terrain" | "satellite">("terrain");
  const [supportedCountMap, setSupportedCountMap] = useState<Record<string, number>>({});
  const [hasSupportedMap, setHasSupportedMap] = useState<Record<string, boolean>>({});

  const handleSupportClick = (issueId: string) => {
    if (hasSupportedMap[issueId]) return;
    setHasSupportedMap(prev => ({ ...prev, [issueId]: true }));
    setSupportedCountMap(prev => ({
      ...prev,
      [issueId]: (prev[issueId] || activeIssue?.supporting_count || 0) + 1
    }));
  };

  const handlePinClick = (issue: any) => {
    setActiveIssue(issue);
    if (onSelectIssue) onSelectIssue(issue);
    if (onPinSelect) onPinSelect(issue);
  };

  return (
    <div className="space-y-4">
      {/* Split-Screen Layout matching User Uploaded UI */}
      <div className="grid grid-cols-1 lg:grid-cols-12 rounded-3xl overflow-hidden border border-[#E7E9E4] shadow-xl bg-[#161E2E]">
        {/* Left Panel: Dark Slate Contact & Issue Details Card */}
        <div className="lg:col-span-5 bg-[#161E2E] text-white p-8 space-y-8 flex flex-col justify-between border-r border-[#2D3B54]">
          <div className="space-y-6">
            {/* Header Title */}
            <div>
              <div className="inline-flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-[#287C73] bg-[#287C73]/15 px-3 py-1 rounded-full border border-[#287C73]/30">
                <Sparkles className="w-3.5 h-3.5" /> Civic Lens GIS Dispatch
              </div>
              <h2 className="text-2xl font-black tracking-tight text-white mt-2">
                ISSUE DETAILS &amp; LOCATION
              </h2>
              <div className="w-12 h-1 bg-[#D94F4F] mt-2 rounded-full" />
            </div>

            <p className="text-xs text-[#94A3B8] font-medium leading-relaxed">
              Real-time PostGIS spatial mapping, responsible authority contact details, and citizen impact counters.
            </p>

            {/* Circular Icon Info Grid matching User Uploaded Image */}
            <div className="space-y-6 pt-2">
              {/* Item 1: Address & Location */}
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-full border-2 border-[#2D3B54] bg-[#0F141C] flex items-center justify-center shrink-0">
                  <MapPin className="w-5 h-5 text-[#287C73]" />
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] font-black text-[#94A3B8] uppercase tracking-wider block">ADDRESS / WARD:</span>
                  <p className="text-xs font-bold text-white leading-snug">
                    {activeIssue?.road || activeIssue?.title || "121 College Road Avenue"}
                  </p>
                  <p className="text-[11px] text-[#94A3B8]">{activeIssue?.ward || "Ward 63, Central District"}</p>
                </div>
              </div>

              {/* Item 2: Email & Department */}
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-full border-2 border-[#2D3B54] bg-[#0F141C] flex items-center justify-center shrink-0">
                  <Mail className="w-5 h-5 text-[#287C73]" />
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] font-black text-[#94A3B8] uppercase tracking-wider block">DEPARTMENT EMAIL:</span>
                  <p className="text-xs font-bold text-[#287C73] underline leading-snug">
                    {activeIssue?.email || "pwd-roads@civiclens.org"}
                  </p>
                  <p className="text-[11px] text-[#94A3B8]">Support &amp; Field Dispatch Cell</p>
                </div>
              </div>

              {/* Item 3: Call Hotline / Officer Contact */}
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-full border-2 border-[#2D3B54] bg-[#0F141C] flex items-center justify-center shrink-0">
                  <Phone className="w-5 h-5 text-[#287C73]" />
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] font-black text-[#94A3B8] uppercase tracking-wider block">RESPONSIBLE AUTHORITY:</span>
                  <p className="text-xs font-bold text-white leading-snug">
                    {activeIssue?.phone || "Municipal Control Desk (Eng. R. K. Patil)"}
                  </p>
                  <p className="text-[11px] text-[#94A3B8]">24/7 Civic Emergency Line</p>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Action Card & Support Button */}
          <div className="bg-[#0F141C] border border-[#2D3B54] rounded-2xl p-4 space-y-3 pt-4">
            <div className="flex items-center justify-between text-xs">
              <span className="text-[#94A3B8] font-medium flex items-center gap-1.5">
                <Users className="w-4 h-4 text-[#287C73]" /> Affected Citizens:
              </span>
              <strong className="text-white font-black text-sm">
                {(supportedCountMap[activeIssue?.id] || activeIssue?.supporting_count || activeIssue?.reports_count || 38)} Citizens
              </strong>
            </div>

            <button
              type="button"
              onClick={() => handleSupportClick(activeIssue?.id)}
              disabled={hasSupportedMap[activeIssue?.id]}
              className={`w-full py-3 rounded-xl font-extrabold text-xs flex items-center justify-center gap-2 transition-all ${
                hasSupportedMap[activeIssue?.id]
                  ? "bg-[#10B981] text-white"
                  : "bg-[#287C73] hover:bg-[#1F645D] text-white shadow-lg teal-glow"
              }`}
            >
              <ThumbsUp className="w-4 h-4" />
              {hasSupportedMap[activeIssue?.id] ? "Supported ✓" : "I am experiencing this issue too"}
            </button>
          </div>
        </div>

        {/* Right Panel: Realistic Geographic Vector Map */}
        <div className="lg:col-span-7 relative h-[540px] bg-[#E5E3DF] overflow-hidden">
          {/* Zoomable Vector Map Canvas */}
          <div
            className="absolute inset-0 transition-transform duration-500 origin-center"
            style={{ transform: `scale(${zoomLevel / 100})` }}
          >
            <svg className="w-full h-full" viewBox="0 0 1000 600" preserveAspectRatio="none">
              {/* Land Base Color */}
              <rect width="1000" height="600" fill={mapLayer === "terrain" ? "#F3F1EC" : "#1A2421"} />

              {/* Water Bodies & Rivers - Soft Muted Civic Teal Blue */}
              <path d="M 0,220 Q 250,160 500,280 T 1000,200 L 1000,600 L 0,600 Z" fill="#C2DADB" opacity="0.9" />

              {/* Coastal Bay / Lake Water */}
              <path d="M 680,0 Q 800,200 1000,220 L 1000,0 Z" fill="#B8D3D5" opacity="0.9" />

              {/* Highway Arterial Roads */}
              <path d="M 120,0 L 880,600" stroke="#F3B83F" strokeWidth="8" />
              <path d="M 120,0 L 880,600" stroke="#FFFFFF" strokeWidth="4" strokeDasharray="16 12" />

              <path d="M 0,320 L 1000,320" stroke="#F3B83F" strokeWidth="7" />
              <path d="M 450,0 L 450,600" stroke="#F3B83F" strokeWidth="6" />

              {/* Secondary Street Networks (White Street Grids) */}
              <path d="M 200,80 L 450,320 M 450,320 L 750,150 M 250,400 L 600,400 M 600,400 L 800,550" stroke="#FFFFFF" strokeWidth="3.5" />

              {/* City District Blocks */}
              <rect x="180" y="90" width="140" height="110" fill="#E1E6DC" opacity="0.8" rx="8" />
              <rect x="520" y="100" width="180" height="130" fill="#D9E2DC" opacity="0.8" rx="8" />
              <rect x="220" y="380" width="200" height="140" fill="#E1E6DC" opacity="0.8" rx="8" />

              {/* Street Labels */}
              <g fill="#4A5568" fontSize="11" fontWeight="bold">
                <text x="230" y="140">College Road Line</text>
                <text x="550" y="150">Market Street Corridor</text>
                <text x="260" y="440">Indira Nagar Link</text>
              </g>
            </svg>

            {/* Interactive Pins */}
            {currentIssuesList.map((issue, idx) => {
              const xPos = issue.x ?? (idx === 0 ? 42 : idx === 1 ? 68 : 30);
              const yPos = issue.y ?? (idx === 0 ? 38 : idx === 1 ? 28 : 72);
              const isSelected = activeIssue?.id === issue.id;

              return (
                <div
                  key={issue.id || idx}
                  onClick={() => handlePinClick(issue)}
                  className="absolute cursor-pointer -translate-x-1/2 -translate-y-1/2 group z-20"
                  style={{ left: `${xPos}%`, top: `${yPos}%` }}
                >
                  {(issue.severity === "Critical" || issue.priority === "P1 — Critical" || isSelected) && (
                    <div className="absolute inset-0 rounded-full bg-[#D94F4F]/40 animate-map-pulse -m-2 pointer-events-none" />
                  )}
                  <div className={`p-2.5 rounded-full border-2 shadow-2xl flex items-center justify-center transition-all ${
                    isSelected
                      ? "bg-[#D94F4F] text-white border-white scale-125 ring-4 ring-[#D94F4F]/40 z-30"
                      : issue.severity === "Critical" || issue.priority === "P1 — Critical"
                      ? "bg-[#D94F4F] text-white border-white animate-bounce"
                      : "bg-[#F3B83F] text-white border-white"
                  }`}>
                    <MapPin className="w-5 h-5" />
                  </div>

                  {/* Hover Label */}
                  <div className="absolute left-1/2 -translate-x-1/2 top-10 hidden group-hover:block bg-[#161E2E] text-white text-[10px] font-extrabold px-3 py-1.5 rounded-xl shadow-xl whitespace-nowrap z-40 border border-[#2D3B54]">
                    {issue.title}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Google Maps Style Location Info Card (Top-Left) */}
          <div className="absolute top-4 left-4 z-30 bg-white/95 backdrop-blur-md border border-[#E7E9E4] rounded-2xl p-3.5 shadow-lg max-w-xs space-y-1">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-black text-[#102C2B]">{activeIssue?.ward || "Central District"}</h3>
              <Navigation className="w-3.5 h-3.5 text-[#287C73]" />
            </div>
            <p className="text-[10px] text-[#4B6363] font-mono">
              {activeIssue?.lat || 19.9975}° N, {activeIssue?.lng || 73.7898}° E • PostGIS
            </p>
            <span className="text-[10px] font-bold text-[#287C73] hover:underline cursor-pointer block">
              View larger map
            </span>
          </div>

          {/* Bottom-Right Zoom Controls matching User Image */}
          <div className="absolute bottom-6 right-6 z-30 flex flex-col bg-white border border-[#E7E9E4] rounded-xl shadow-xl overflow-hidden">
            <button
              type="button"
              onClick={() => setZoomLevel(prev => Math.min(250, prev + 25))}
              className="p-2.5 hover:bg-[#F7F6F2] text-[#102C2B] border-b border-[#E7E9E4]"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setZoomLevel(prev => Math.max(100, prev - 25))}
              className="p-2.5 hover:bg-[#F7F6F2] text-[#102C2B]"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
          </div>

          {/* Bottom-Left Satellite Layer Switcher Thumbnail matching User Image */}
          <div
            onClick={() => setMapLayer(prev => prev === "terrain" ? "satellite" : "terrain")}
            className="absolute bottom-6 left-6 z-30 w-12 h-12 rounded-xl overflow-hidden border-2 border-white shadow-xl cursor-pointer hover:scale-105 transition-transform bg-[#102C2B] flex items-center justify-center"
          >
            <span className="text-[10px] font-black text-white text-center leading-tight">
              {mapLayer === "terrain" ? "🛰️ Sat" : "🗺️ Map"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
