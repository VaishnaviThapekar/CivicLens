"use client";

import { useState, useEffect } from "react";
import { Camera, Sparkles, MapPin, Eye, CheckCircle2, ShieldCheck, Crosshair } from "lucide-react";

export default function ARDefectScanner() {
  const [scanning, setScanning] = useState(true);
  const [defectInfo, setDefectInfo] = useState<any>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setScanning(false);
      setDefectInfo({
        category: "Deep Road Surface Pothole",
        confidence: "98.4% AI Match",
        estimated_area: "14.5 m²",
        severity: "CRITICAL P1",
        coords: "19.9975° N, 73.7898° E",
        depth_est: "12.4 cm"
      });
    }, 2200);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative w-full h-80 sm:h-96 rounded-3xl overflow-hidden shadow-2xl border-2 border-[#287C73] bg-[#0F141C] text-white">
      {/* Background Real-World Civic Camera View */}
      <img
        src="https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=1000&q=80"
        alt="AR Camera Viewport"
        className="w-full h-full object-cover opacity-80"
      />

      {/* AR HUD Overlay Lines */}
      <div className="absolute inset-0 border-[6px] border-emerald-400/40 rounded-3xl pointer-events-none" />

      {/* Scanning Target Reticle */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border-2 border-emerald-400 border-dashed rounded-2xl flex items-center justify-center animate-pulse pointer-events-none">
        <Crosshair className="w-10 h-10 text-emerald-400 animate-spin" />
        <span className="absolute -top-6 text-[10px] font-mono text-emerald-400 font-bold bg-black/70 px-2 py-0.5 rounded">
          AR DEPTH SENSOR ACTIVE
        </span>
      </div>

      {/* Top HUD Metrics Bar */}
      <div className="absolute top-4 left-4 right-4 flex items-center justify-between bg-black/60 backdrop-blur-md px-4 py-2 rounded-2xl border border-white/20 text-xs font-mono">
        <div className="flex items-center gap-2 text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>REAL-TIME AR SCANNER</span>
        </div>
        <span className="text-gray-300">LAT: 19.9975 | LNG: 73.7898</span>
      </div>

      {/* Bottom AR Detection Card */}
      {defectInfo && (
        <div className="absolute bottom-4 left-4 right-4 bg-[#102C2B]/90 backdrop-blur-md border border-[#287C73] p-4 rounded-2xl space-y-2 animate-fade-in">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-[#F3B83F] flex items-center gap-1">
              <Sparkles className="w-4 h-4" /> {defectInfo.confidence}
            </span>
            <span className="text-xs font-black bg-red-500/20 text-red-400 px-2.5 py-0.5 rounded-full border border-red-500/30">
              {defectInfo.severity}
            </span>
          </div>

          <div className="flex justify-between items-end">
            <div>
              <h4 className="text-sm font-black text-white">{defectInfo.category}</h4>
              <p className="text-[11px] text-gray-300">Area: {defectInfo.estimated_area} • Depth: {defectInfo.depth_est}</p>
            </div>
            <span className="text-[11px] font-bold text-emerald-400 bg-emerald-400/15 px-3 py-1 rounded-full border border-emerald-400/30">
              ✓ Ready for Dispatch
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
