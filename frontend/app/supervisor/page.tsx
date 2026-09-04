"use client";

import { useEffect, useState } from "react";
import {
  ShieldAlert, ShieldCheck, UserCheck, AlertTriangle, FileText,
  Award, RefreshCw, Sparkles, Building2, AlertCircle, Download, CheckCircle2
} from "lucide-react";

export default function SupervisorPortal() {
  const [contractors, setContractors] = useState<any[]>([]);
  const [auditLog, setAuditLog] = useState<any>(null);
  const [cpgramsResult, setCpgramsResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadSupervisorData = async () => {
    setLoading(true);
    try {
      const cRes = await fetch("http://localhost:8000/api/supervisor/contractors");
      const aRes = await fetch("http://localhost:8000/api/supervisor/audit-log");
      if (cRes.ok) setContractors(await cRes.json());
      if (aRes.ok) setAuditLog(await aRes.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSupervisorData();
  }, []);

  const handleSyncCPGRAMS = async (complaintId: string = "c-101") => {
    try {
      const res = await fetch(`http://localhost:8000/api/supervisor/cpgrams/sync/${complaintId}`, {
        method: "POST"
      });
      if (res.ok) {
        setCpgramsResult(await res.json());
      }
    } catch (err) {
      alert("CPGRAMS Sync error");
    }
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in text-white">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-[#161E2E] border border-[#2D3B54] p-6 rounded-3xl shadow-md">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-[#287C73] uppercase tracking-wider bg-[#287C73]/15 px-3 py-1 rounded-full border border-[#287C73]/30">
            <Award className="w-4 h-4 text-[#287C73]" /> Features 04 &amp; 05: Contractor Scorecard &amp; CPGRAMS Portal Sync
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white">Supervisor Audit &amp; Contractor Transparency</h1>
          <p className="text-xs text-[#94A3B8]">
            Contractor SLA ratings, penalty deductions (₹25,000 per breach), anti-fraud EXIF/dHash audits, and 1-click CPGRAMS Sync.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="http://localhost:8000/api/intelligence/export-audit-pdf"
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 rounded-xl bg-[#287C73] hover:bg-[#1F645D] text-white text-xs font-bold flex items-center gap-2 border border-[#287C73]"
          >
            📄 Download Audit (PDF) &rarr;
          </a>

          <button
            onClick={loadSupervisorData}
            className="px-4 py-2 rounded-xl bg-[#1F293D] hover:bg-[#2D3B54] text-white text-xs font-semibold flex items-center gap-2 border border-[#2D3B54]"
          >
            <RefreshCw className="w-4 h-4 text-[#287C73]" /> Refresh Audit Data
          </button>
        </div>
      </div>

      {/* Contractor Penalty Tracker & Quality Scorecard */}
      <div className="bg-[#161E2E] border border-[#2D3B54] rounded-3xl p-6 space-y-4 shadow-sm">
        <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Building2 className="w-4 h-4 text-[#287C73]" /> Municipal Contractor Quality &amp; SLA Penalty Scorecard
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#F8FAFC]">
            <thead className="bg-[#0F141C] text-[#94A3B8] uppercase font-semibold border-b border-[#2D3B54]">
              <tr>
                <th className="p-3">Contractor ID</th>
                <th className="p-3">Company Name</th>
                <th className="p-3">Department</th>
                <th className="p-3">Assigned</th>
                <th className="p-3">AI Pass Rate</th>
                <th className="p-3">Fake Flags</th>
                <th className="p-3">Penalty Deductions</th>
                <th className="p-3 text-right">Rating</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#2D3B54]">
              {contractors.map((row, idx) => (
                <tr key={idx} className="hover:bg-[#1F293D]">
                  <td className="p-3 font-mono font-bold text-[#287C73]">{row.contractor_id}</td>
                  <td className="p-3 font-bold text-white">{row.name}</td>
                  <td className="p-3 text-[#94A3B8]">{row.department}</td>
                  <td className="p-3">{row.total_assigned}</td>
                  <td className="p-3 font-semibold text-[#10B981]">{row.ai_verification_pass_rate}%</td>
                  <td className="p-3 font-bold text-red-400">{row.fake_flag_count}</td>
                  <td className="p-3 font-mono font-extrabold text-amber-400">{row.sla_breach_penalties_inr || "₹0"}</td>
                  <td className="p-3 text-right">
                    <span className="px-2.5 py-1 rounded font-bold bg-[#287C73]/20 text-[#287C73] border border-[#287C73]/30">
                      {row.quality_rating}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Anti-Fraud Fake Resolution Audit Log */}
        <div className="lg:col-span-6 bg-[#161E2E] border border-[#2D3B54] rounded-3xl p-6 space-y-4">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center justify-between">
            <span className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-400" /> Flagged Fake Resolutions Audit Log
            </span>
            <span className="text-red-400 font-bold">
              {auditLog?.fake_resolution_audits?.length || 0} Flags
            </span>
          </h2>

          <div className="space-y-3">
            {auditLog?.fake_resolution_audits?.map((flag: any, i: number) => (
              <div key={i} className="bg-[#0F141C] border border-red-500/30 p-4 rounded-xl space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-red-400 font-bold">{flag.tracking_number}</span>
                  <span className="text-[#94A3B8]">{flag.officer_assigned}</span>
                </div>
                <p className="text-white font-semibold">{flag.reason}</p>
                <div className="flex items-center justify-between pt-2 border-t border-[#2D3B54] text-[#94A3B8]">
                  <span>AI Score: <strong className="text-red-400">{flag.ai_score}%</strong></span>
                  <button onClick={() => handleSyncCPGRAMS(flag.complaint_id)} className="text-[#287C73] hover:underline font-semibold">
                    Sync to CPGRAMS &rarr;
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CPGRAMS National Portal Sync Panel */}
        <div className="lg:col-span-6 bg-[#161E2E] border border-[#2D3B54] rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#287C73]" /> CPGRAMS National Portal Synchronization
            </h2>
            <button
              onClick={() => handleSyncCPGRAMS("c-101")}
              className="text-xs px-3.5 py-2 rounded-xl bg-[#287C73] hover:bg-[#1F645D] text-white font-bold flex items-center gap-1.5 shadow-md"
            >
              <Download className="w-3.5 h-3.5" /> 1-Click Sync CPGRAMS
            </button>
          </div>

          {cpgramsResult ? (
            <div className="bg-[#0F141C] border border-[#287C73]/40 p-4 rounded-2xl text-xs space-y-3 font-mono text-[#F8FAFC]">
              <div className="text-[#10B981] font-bold border-b border-[#2D3B54] pb-2 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> {cpgramsResult.message}
              </div>
              <p><strong className="text-[#94A3B8]">CPGRAMS Reg ID:</strong> {cpgramsResult.cpgrams_dossier?.cpgrams_registration_id}</p>
              <p><strong className="text-[#94A3B8]">Ministry:</strong> {cpgramsResult.cpgrams_dossier?.ministry_department}</p>
              <p><strong className="text-[#94A3B8]">Status:</strong> {cpgramsResult.cpgrams_dossier?.sync_status}</p>
            </div>
          ) : (
            <div className="text-center py-16 text-[#94A3B8] text-xs">
              Click <strong>"1-Click Sync CPGRAMS"</strong> to synchronize municipal complaints with the National Grievance Portal.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
