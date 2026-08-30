"use client";

import { Award, ShieldCheck, CheckCircle2, Download, QrCode } from "lucide-react";

interface CertificateProps {
  userName?: string;
  karmaPoints?: number;
  ward?: string;
}

export default function CivicCertificate({
  userName = "Alex Morgan",
  karmaPoints = 4850,
  ward = "Ward 63 (College Road)"
}: CertificateProps) {
  return (
    <div className="bg-white border-4 border-[#287C73] rounded-3xl p-8 shadow-2xl relative overflow-hidden space-y-6 text-[#102C2B] max-w-2xl mx-auto">
      {/* Decorative Corner Accents */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-[#287C73]/10 rounded-bl-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-[#287C73]/10 rounded-tr-full pointer-events-none" />

      {/* Certificate Header */}
      <div className="text-center space-y-2 border-b border-[#E7E9E4] pb-6">
        <div className="w-14 h-14 rounded-2xl bg-[#287C73] text-white flex items-center justify-center mx-auto shadow-lg teal-glow font-black text-2xl">
          🏛️
        </div>
        <span className="text-[11px] font-black uppercase tracking-widest text-[#287C73] block">
          CENTRAL MUNICIPAL CORPORATION • CIVIC INTELLIGENCE DIVISION
        </span>
        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-[#102C2B]">
          Certificate of Civic Distinction
        </h2>
        <p className="text-xs text-[#4B6363] font-semibold">Official Governance &amp; Community Leadership Recognition</p>
      </div>

      {/* Recipient Details */}
      <div className="text-center space-y-3 py-2">
        <p className="text-xs text-[#4B6363] font-medium">This official civic distinction is awarded to</p>
        <h3 className="text-3xl font-black text-[#287C73] tracking-wide uppercase border-b-2 border-[#287C73] inline-block pb-1">
          {userName}
        </h3>
        <p className="text-xs text-[#4B6363] font-semibold max-w-md mx-auto leading-relaxed">
          For outstanding civic engagement, logging 24 verified urban grievance reports, and earning <strong className="text-[#102C2B]">{karmaPoints.toLocaleString()} Civic Karma Points</strong> in {ward}.
        </p>
      </div>

      {/* Gold Seal & Verification QR Code Footer */}
      <div className="pt-4 border-t border-[#E7E9E4] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-[#F3B83F]/20 text-[#F3B83F] border-2 border-[#F3B83F] flex items-center justify-center font-black text-xl shadow-md">
            👑
          </div>
          <div>
            <span className="text-[10px] font-black uppercase text-[#102C2B] block">OFFICIAL MUNICIPAL SEAL</span>
            <span className="text-[9px] text-[#4B6363]">Verified by AI Vision &amp; Ward Supervisor</span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] font-mono text-[#4B6363] block">ID: CERT-CL-2026-99201</span>
          <span className="text-[10px] text-[#10B981] font-extrabold flex items-center gap-1 justify-end">
            <CheckCircle2 className="w-3 h-3" /> Blockchain Verified
          </span>
        </div>
      </div>
    </div>
  );
}
