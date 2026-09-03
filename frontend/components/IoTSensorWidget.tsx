"use client";

import { useEffect, useState } from "react";
import { Activity, Droplets, Gauge, AlertTriangle, ShieldCheck } from "lucide-react";

export default function IoTSensorWidget() {
  const [pressure, setPressure] = useState(4.2);
  const [vibration, setVibration] = useState(12.4);

  useEffect(() => {
    const timer = setInterval(() => {
      setPressure((prev) => +(prev + (Math.random() * 0.2 - 0.1)).toFixed(2));
      setVibration((prev) => +(prev + (Math.random() * 0.4 - 0.2)).toFixed(2));
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-4 shadow-sm text-[#102C2B] hover-lift">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-[#287C73] animate-pulse" />
          <h3 className="font-black text-sm text-[#102C2B]">IoT Sub-Surface Sensor Telemetry</h3>
        </div>
        <span className="text-[10px] font-bold bg-emerald-50 text-emerald-700 px-2.5 py-0.5 rounded-full border border-emerald-200">
          NODE #NODE-W63-4
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#F7F6F2] p-4 rounded-2xl space-y-1">
          <span className="text-xs text-[#4B6363] font-bold flex items-center gap-1">
            <Gauge className="w-3.5 h-3.5 text-[#287C73]" /> Pipe Pressure
          </span>
          <div className="text-2xl font-black text-[#102C2B]">{pressure} <span className="text-xs font-normal">Bar</span></div>
          <span className="text-[10px] text-emerald-600 font-extrabold">✓ Normal Flow Range</span>
        </div>

        <div className="bg-[#F7F6F2] p-4 rounded-2xl space-y-1">
          <span className="text-xs text-[#4B6363] font-bold flex items-center gap-1">
            <Droplets className="w-3.5 h-3.5 text-[#287C73]" /> Acoustic Freq
          </span>
          <div className="text-2xl font-black text-[#102C2B]">{vibration} <span className="text-xs font-normal">Hz</span></div>
          <span className="text-[10px] text-[#287C73] font-extrabold">Sub-surface Leak Scan Clean</span>
        </div>
      </div>
    </div>
  );
}
