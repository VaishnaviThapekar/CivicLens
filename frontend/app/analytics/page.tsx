"use client";

import { useEffect, useState } from "react";
import { BarChart3, Zap, ShieldAlert, TrendingUp, AlertTriangle, Activity, Wifi, Radio, Plane, Truck, Wrench, Layers } from "lucide-react";
import { fetchPredictiveRisks } from "@/lib/api";
import CPGRAMSSyncBadge from "@/components/CPGRAMSSyncBadge";
import IoTSensorWidget from "@/components/IoTSensorWidget";

export default function PredictiveAnalyticsPage() {
  const [risks, setRisks] = useState<any[]>([]);
  const [materials, setMaterials] = useState<any>(null);
  const [thermalLeaks, setThermalLeaks] = useState<any>(null);

  useEffect(() => {
    async function loadData() {
      const data = await fetchPredictiveRisks();
      setRisks(data);

      try {
        const mRes = await fetch("http://localhost:8000/api/intelligence/material-quantify");
        const tRes = await fetch("http://localhost:8000/api/intelligence/thermal-leaks");
        if (mRes.ok) setMaterials(await mRes.json());
        if (tRes.ok) setThermalLeaks(await tRes.json());
      } catch (e) {
        console.error("Telemetry fetch error", e);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8 pb-12 animate-fade-in text-[#102C2B]">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-white border border-[#E7E9E4] p-6 rounded-3xl shadow-sm">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3 py-1 rounded-full border border-[#287C73]/20">
            <Zap className="w-4 h-4 text-[#287C73]" /> AI Material Quantifier &amp; Thermal Leak Telemetry
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-[#102C2B]">Predictive Civic &amp; IoT Telemetry Engine</h1>
          <p className="text-xs text-[#4B6363]">
            Sub-surface thermal leak infrared scans, CV material quantity calculation, and field repair squad route optimization.
          </p>
        </div>
      </div>

      {/* Real-Time IoT & National CPGRAMS Webhook Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <CPGRAMSSyncBadge />
        <IoTSensorWidget />
      </div>

      {/* AI Material Quantifier & Automated Dispatch Engine */}
      {materials && (
        <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-[#102C2B] uppercase tracking-wider flex items-center gap-2">
              <Truck className="w-4 h-4 text-[#287C73]" /> AI Material Quantifier &amp; Repair Squad Dispatch
            </h2>
            <span className="text-xs font-bold font-mono text-[#10B981] bg-[#10B981]/10 px-3 py-1 rounded-full border border-[#10B981]/20">
              Est. Repair Cost: {materials.estimated_cost_inr}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#F7F6F2] p-4 rounded-2xl border border-[#E7E9E4] space-y-1">
              <span className="text-[10px] text-[#4B6363] font-bold block">COLD MIX ASPHALT</span>
              <strong className="text-xl text-[#287C73]">{materials.materials?.cold_mix_asphalt_tons} Tons</strong>
              <p className="text-[11px] text-[#4B6363]">Auto-calculated from CV 14.5m² bounding box.</p>
            </div>

            <div className="bg-[#F7F6F2] p-4 rounded-2xl border border-[#E7E9E4] space-y-1">
              <span className="text-[10px] text-[#4B6363] font-bold block">CONCRETE VOLUME</span>
              <strong className="text-xl text-[#10B981]">{materials.materials?.concrete_volume_m3} m³</strong>
              <p className="text-[11px] text-[#4B6363]">Foundation compaction grade cement.</p>
            </div>

            <div className="bg-[#F7F6F2] p-4 rounded-2xl border border-[#E7E9E4] space-y-1">
              <span className="text-[10px] text-[#4B6363] font-bold block">RECOMMENDED EQUIPMENT</span>
              <strong className="text-xs text-[#102C2B] block truncate">{materials.recommended_equipment?.join(", ")}</strong>
              <p className="text-[11px] text-[#4B6363]">Automated PWD Depot #4 requisition.</p>
            </div>
          </div>

          {/* Dispatch Route Stops */}
          <div className="bg-[#F7F6F2] p-4 rounded-2xl border border-[#E7E9E4] space-y-2">
            <span className="text-xs font-bold text-[#102C2B] flex items-center gap-1.5">
              <Wrench className="w-3.5 h-3.5 text-[#287C73]" /> Optimized Dispatch Route ({materials.dispatch_route?.crew_assigned}):
            </span>
            <ul className="space-y-1 text-xs text-[#4B6363] font-mono">
              {materials.dispatch_route?.route_stops?.map((stop: string, idx: number) => (
                <li key={idx}>• {stop}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Sub-Surface Thermal & Infrastructure Leak Prediction */}
      {thermalLeaks && (
        <div className="space-y-4">
          <h2 className="text-xs font-bold text-[#102C2B] uppercase tracking-wider flex items-center gap-2">
            <Radio className="w-4 h-4 text-[#D94F4F]" /> Sub-Surface Thermal &amp; Pipe Leak Collapse Warning
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {thermalLeaks.anomalies_detected?.map((leak: any, i: number) => (
              <div key={i} className="bg-white border border-[#D94F4F]/30 p-5 rounded-2xl space-y-3 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-[#D94F4F]">{leak.scan_id}</span>
                  <span className="text-xs font-extrabold bg-[#D94F4F]/10 text-[#D94F4F] px-2.5 py-0.5 rounded-full">
                    {leak.leak_probability} Collapse Risk
                  </span>
                </div>
                <h3 className="font-bold text-sm text-[#102C2B]">{leak.location}</h3>
                <p className="text-xs text-[#4B6363]">{leak.recommended_action}</p>

                <div className="pt-2 border-t border-[#E7E9E4] flex justify-between text-xs font-mono text-[#4B6363]">
                  <span>Thermal Variance: <strong className="text-[#D94F4F]">{leak.sub_surface_temp_variance}</strong></span>
                  <span>Prevention Window: <strong className="text-[#F3B83F]">{leak.time_to_potential_collapse_hours}h remaining</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Predictive Warnings */}
      <div className="space-y-4">
        <h2 className="text-xs font-bold text-[#102C2B] uppercase tracking-wider flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-[#F3B83F]" /> Active Predictive Hazard Warnings
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {risks.map((risk) => (
            <div key={risk.id} className="bg-white border border-[#F3B83F]/30 p-6 rounded-3xl space-y-3 shadow-sm text-[#102C2B]">
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#F3B83F] text-xs flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" /> {risk.zone} • {risk.hazard_type}
                </span>
                <span className="font-extrabold text-[#D94F4F] text-xs font-mono">{Math.round(risk.probability * 100)}% Risk</span>
              </div>

              <h3 className="text-base font-extrabold text-[#102C2B]">{risk.hazard_type}</h3>
              <p className="text-xs text-[#4B6363] leading-relaxed">{risk.recommended_action}</p>

              <div className="pt-2 border-t border-[#E7E9E4] flex justify-between text-xs">
                <span className="text-[#4B6363]">Historical Correlation:</span>
                <span className="font-bold text-[#287C73]">{risk.historical_correlation}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
