"use client";

import { useEffect, useState } from "react";
import { RefreshCw, CheckCircle2, ArrowUpRight, ShieldCheck } from "lucide-react";

export default function CPGRAMSSyncBadge() {
  const [syncStatus, setSyncStatus] = useState({
    last_sync: "Just now",
    cpgrams_id: "CPGRAMS-NMC-2026-88102",
    status: "SYNCED_2WAY",
    total_synced: 1420
  });
  const [syncing, setSyncing] = useState(false);

  const handleManualSync = () => {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
      setSyncStatus((prev) => ({
        ...prev,
        last_sync: "Just now",
        total_synced: prev.total_synced + 1
      }));
    }, 1200);
  };

  return (
    <div className="bg-[#102C2B] text-white p-5 rounded-3xl border border-[#287C73]/40 shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">🇮🇳</span>
          <div>
            <span className="text-[10px] font-black uppercase text-[#F3B83F] tracking-wider block">
              NATIONAL CPGRAMS SYNC PORTAL
            </span>
            <h4 className="font-extrabold text-sm text-white">Bidirectional Webhook Sync</h4>
          </div>
        </div>

        <button
          type="button"
          onClick={handleManualSync}
          disabled={syncing}
          className="p-2 rounded-xl bg-[#287C73] hover:bg-[#1F645D] text-white text-xs font-bold transition-all shadow-md"
          title="Force Webhook Sync"
        >
          <RefreshCw className={`w-4 h-4 ${syncing ? "animate-spin" : ""}`} />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs pt-1 border-t border-[#287C73]/30">
        <div className="bg-white/10 p-2.5 rounded-xl">
          <span className="text-[10px] text-gray-300 block">CPGRAMS ID</span>
          <strong className="text-emerald-400 font-mono">{syncStatus.cpgrams_id}</strong>
        </div>

        <div className="bg-white/10 p-2.5 rounded-xl">
          <span className="text-[10px] text-gray-300 block">Sync Status</span>
          <strong className="text-emerald-400 font-extrabold flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> Live 2-Way
          </strong>
        </div>
      </div>

      <div className="flex justify-between items-center text-[11px] text-gray-300 pt-1">
        <span>Synced Tickets: <strong className="text-white">{syncStatus.total_synced.toLocaleString()}</strong></span>
        <span className="text-[#F3B83F]">Last sync: {syncStatus.last_sync}</span>
      </div>
    </div>
  );
}
