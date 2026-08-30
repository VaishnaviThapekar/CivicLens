"use client";

import { useEffect, useState } from "react";
import { Award, ShieldAlert, CheckCircle2, AlertTriangle, Building, ShieldCheck, FileCheck } from "lucide-react";

export default function ContractorScorecardPage() {
  const [contractors, setContractors] = useState<any[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await fetch("http://localhost:8000/api/intelligence/governance/contractors");
        if (res.ok) setContractors(await res.json());
      } catch (e) {
        console.error("Contractor fetch error", e);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8 pb-12 animate-fade-in text-[#102C2B]">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-white border border-[#E7E9E4] p-6 rounded-3xl shadow-sm">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3 py-1 rounded-full border border-[#287C73]/20">
            <Building className="w-4 h-4 text-[#287C73]" /> Municipal Contractor Quality &amp; Audit Scorecard
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-[#102C2B]">Contractor Rating &amp; SLA Compliance</h1>
          <p className="text-xs text-[#4B6363]">
            Automated quality audit scoring third-party repair contractors on AI vision pass rate, repair durability, and SLA compliance.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {contractors.map((c) => (
          <div key={c.id} className="bg-white border border-[#E7E9E4] p-6 rounded-3xl space-y-4 shadow-sm hover-lift">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black uppercase text-[#287C73] bg-[#287C73]/10 px-2.5 py-0.5 rounded border border-[#287C73]/20">
                {c.id}
              </span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                c.status === "RATED_EXCELLENT" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" :
                c.status === "RATED_GOOD" ? "bg-amber-50 text-amber-700 border border-amber-200" : "bg-red-50 text-red-700 border border-red-200"
              }`}>
                {c.status}
              </span>
            </div>

            <h3 className="font-extrabold text-sm text-[#102C2B]">{c.name}</h3>
            <p className="text-xs text-[#4B6363]">Assigned: <strong>{c.ward_assigned}</strong></p>

            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-[#E7E9E4] text-xs">
              <div className="bg-[#F7F6F2] p-2.5 rounded-xl">
                <span className="text-[10px] text-[#4B6363] block">AI Pass Rate</span>
                <strong className="text-emerald-700 font-extrabold">{c.ai_vision_pass_rate}</strong>
              </div>

              <div className="bg-[#F7F6F2] p-2.5 rounded-xl">
                <span className="text-[10px] text-[#4B6363] block">Durability Score</span>
                <strong className="text-[#287C73] font-extrabold">{c.durability_score}</strong>
              </div>
            </div>

            <div className="flex justify-between text-xs pt-1">
              <span className="text-[#4B6363]">Completed Jobs: <strong>{c.completed_jobs}</strong></span>
              <span className="text-[#4B6363]">Penalties Issued: <strong className="text-red-600">{c.penalties_issued}</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
