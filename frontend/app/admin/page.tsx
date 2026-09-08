"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Cpu, Terminal, Users, Database, Shield, Check, Play, MapPin } from "lucide-react";
import { fetchUserProfile } from "@/lib/api";

const SYSTEM_ROLES = [
  { role: "Citizen", desc: "Report issues via photo/voice/video, track ticket timeline, confirm resolution." },
  { role: "Volunteer", desc: "Verify ground reports, add localized landmark notes, assist elderly citizens." },
  { role: "Officer", desc: "Accept priority dispatches (P1-P4), upload repair evidence, execute resolution." },
  { role: "Supervisor", desc: "Audit contractor performance, review fake resolution flags, export CPGRAMS dossiers." },
  { role: "Administrator", desc: "Configure system rules, manage division routing schemas, manage GIS boundaries." },
  { role: "Analyst", desc: "Run PostGIS spatial queries, inspect predictive risk heatmaps, track SLA metrics." }
];

export default function AdminConsole() {
  const router = useRouter();
  const [activeRole, setActiveRole] = useState("Administrator");
  const [sqlQuery, setSqlQuery] = useState("SELECT * FROM civic_incidents WHERE ST_DWithin(geom, ST_SetSRID(ST_Point(73.7898, 19.9975), 4326), 0.005);");
  const [queryOutput, setQueryOutput] = useState<any>(null);
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    const verifyAccess = async () => {
      try {
        const u = await fetchUserProfile();
        const r = u.role?.value || u.role || "";
        if (r !== "Administrator" && r !== "Supervisor") {
          router.push("/auth");
          return;
        }
      } catch {
        const stored = localStorage.getItem("civiclens_user");
        if (!stored) {
          router.push("/auth");
          return;
        }
      }
    };
    verifyAccess();
  }, []);

  const handleExecuteSql = () => {
    setExecuting(true);
    setTimeout(() => {
      setQueryOutput({
        status: "200 OK",
        execution_time: "1.42 ms",
        postgis_function: "ST_DWithin(geometry, geometry, float)",
        srid: 4326,
        rows_returned: 12,
        matching_incidents: [
          { id: "CL-2026-00101", ward: "Ward 63", dist_meters: 14.2, status: "Resolved" },
          { id: "CL-2026-00103", ward: "Ward 63", dist_meters: 38.6, status: "Clustered" },
          { id: "CL-2026-00106", ward: "Ward 63", dist_meters: 42.1, status: "Submitted" }
        ]
      });
      setExecuting(false);
    }, 400);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-[#161E2E] border border-[#2D3B54] p-6 rounded-3xl shadow-md">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-[#0F766E] uppercase tracking-wider bg-[#0F766E]/10 px-2.5 py-1 rounded-full border border-[#0F766E]/20">
            <Cpu className="w-4 h-4 text-[#0F766E]" /> PostGIS &amp; Role Management Console
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white">Admin &amp; Spatial Intelligence</h1>
          <p className="text-xs text-[#94A3B8]">
            Switch between 6 system roles and execute spatial PostGIS SQL query benchmarks.
          </p>
        </div>
      </div>

      {/* 6 System Roles Grid */}
      <div className="bg-[#161E2E] border border-[#2D3B54] rounded-3xl p-6 space-y-4 shadow-sm">
        <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Users className="w-4 h-4 text-[#0F766E]" /> System Role Architecture (6 Roles)
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {SYSTEM_ROLES.map((item) => (
            <div
              key={item.role}
              onClick={() => setActiveRole(item.role)}
              className={`p-4 rounded-2xl border text-xs cursor-pointer transition-all space-y-2 ${
                activeRole === item.role
                  ? "bg-[#1F293D] border-[#0F766E] text-white shadow-lg teal-glow"
                  : "bg-[#0F141C] border-[#2D3B54] text-[#94A3B8] hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{item.role}</span>
                {activeRole === item.role && <Check className="w-4 h-4 text-[#0F766E]" />}
              </div>
              <p className="text-[11px] leading-relaxed text-[#94A3B8]">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* PostGIS SQL Query Console */}
      <div className="bg-[#161E2E] border border-[#2D3B54] rounded-3xl p-6 space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Terminal className="w-4 h-4 text-[#0F766E]" /> Interactive PostGIS Spatial Terminal
          </h2>
          <span className="text-[10px] font-mono text-[#0F766E] bg-[#0F766E]/10 px-2 py-0.5 rounded border border-[#0F766E]/20">
            SRID 4326 (WGS 84)
          </span>
        </div>

        <div className="space-y-3">
          <textarea
            rows={3}
            value={sqlQuery}
            onChange={(e) => setSqlQuery(e.target.value)}
            className="w-full bg-[#0F141C] border border-[#2D3B54] rounded-xl p-3 text-xs font-mono text-[#10B981] focus:outline-none focus:border-[#0F766E]"
          />

          <button
            onClick={handleExecuteSql}
            disabled={executing}
            className="px-5 py-2.5 rounded-xl bg-[#0F766E] hover:bg-[#0D655E] text-white font-extrabold text-xs shadow flex items-center gap-2 teal-glow"
          >
            <Play className="w-3.5 h-3.5" /> Execute PostGIS Spatial Query
          </button>
        </div>

        {queryOutput && (
          <div className="bg-[#0F141C] border border-[#2D3B54] p-4 rounded-2xl space-y-2 text-xs font-mono">
            <div className="text-[#10B981] font-bold flex justify-between border-b border-[#2D3B54] pb-2">
              <span>Status: {queryOutput.status}</span>
              <span>Execution Time: {queryOutput.execution_time}</span>
            </div>
            <p className="text-[#94A3B8]">Function: {queryOutput.postgis_function}</p>
            <p className="text-[#94A3B8]">Matching spatial rows within 500m radius: {queryOutput.rows_returned}</p>
          </div>
        )}
      </div>
    </div>
  );
}
