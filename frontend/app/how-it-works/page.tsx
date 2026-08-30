import Link from "next/link";
import { Sparkles, Camera, MapPin, Eye, Zap, CheckCircle2, ArrowRight } from "lucide-react";

export default function HowItWorksPage() {
  return (
    <div className="max-w-5xl mx-auto space-y-16 pb-16 animate-fade-in text-[#102C2B]">
      <div className="text-center space-y-3">
        <span className="text-xs font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3.5 py-1 rounded-full border border-[#287C73]/20">
          The Civic AI Pipeline Engine
        </span>
        <h1 className="text-4xl font-black text-[#102C2B]">How CivicLens Works</h1>
        <p className="text-base text-[#4B6363] font-medium max-w-2xl mx-auto">
          An end-to-end intelligence loop connecting citizen evidence, computer vision, spatial clustering, and closed-loop resolution verification.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Step 1 */}
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-sm space-y-4 hover-lift">
          <div className="h-44 rounded-2xl overflow-hidden border border-[#E7E9E4] relative">
            <img
              src="https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=800&q=80"
              alt="Multimodal Evidence"
              className="w-full h-full object-cover"
            />
            <span className="absolute top-3 left-3 bg-[#287C73] text-white text-xs font-black px-3 py-1 rounded-full shadow-md">
              01 • EVIDENCE CAPTURE
            </span>
          </div>
          <h2 className="text-lg font-black text-[#102C2B]">Multimodal Evidence Capture</h2>
          <p className="text-xs text-[#4B6363] font-medium leading-relaxed">
            Citizens snap a photo, record audio in Marathi/Hindi/English, or upload short video clips. Bhashini / Whisper STT models transcribe voice intent in real time with automatic GPS tagging.
          </p>
        </div>

        {/* Step 2 */}
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-sm space-y-4 hover-lift">
          <div className="h-44 rounded-2xl overflow-hidden border border-[#E7E9E4] relative">
            <img
              src="https://images.unsplash.com/photo-1578991624414-276ef23a534f?auto=format&fit=crop&w=800&q=80"
              alt="Computer Vision Defect Area"
              className="w-full h-full object-cover"
            />
            <span className="absolute top-3 left-3 bg-[#287C73] text-white text-xs font-black px-3 py-1 rounded-full shadow-md">
              02 • COMPUTER VISION
            </span>
          </div>
          <h2 className="text-lg font-black text-[#102C2B]">Computer Vision &amp; Area Estimation</h2>
          <p className="text-xs text-[#4B6363] font-medium leading-relaxed">
            PyTorch / YOLOv8 vision pipeline identifies defect categories (Potholes, Waste Dumps, Pipeline Leakage), draws bounding box overlays, and calculates surface area in m².
          </p>
        </div>

        {/* Step 3 */}
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-sm space-y-4 hover-lift">
          <div className="h-44 rounded-2xl overflow-hidden border border-[#E7E9E4] relative">
            <img
              src="https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&w=800&q=80"
              alt="GIS Spatial Cluster"
              className="w-full h-full object-cover"
            />
            <span className="absolute top-3 left-3 bg-[#287C73] text-white text-xs font-black px-3 py-1 rounded-full shadow-md">
              03 • SPATIAL CLUSTERING
            </span>
          </div>
          <h2 className="text-lg font-black text-[#102C2B]">Spatial Clustering &amp; Dispatch</h2>
          <p className="text-xs text-[#4B6363] font-medium leading-relaxed">
            DBSCAN spatial clustering merges multiple duplicate reports within 250m into one incident, while multi-hazard cross-correlation identifies systemic root causes (*e.g. Drainage Pipe Collapse*).
          </p>
        </div>

        {/* Step 4 */}
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-6 shadow-sm space-y-4 hover-lift">
          <div className="h-44 rounded-2xl overflow-hidden border border-[#E7E9E4] relative">
            <img
              src="https://images.unsplash.com/photo-1509114397022-ed747cca3f65?auto=format&fit=crop&w=800&q=80"
              alt="Resolution Audit Verification"
              className="w-full h-full object-cover"
            />
            <span className="absolute top-3 left-3 bg-[#287C73] text-white text-xs font-black px-3 py-1 rounded-full shadow-md">
              04 • AI RESOLUTION AUDIT
            </span>
          </div>
          <h2 className="text-lg font-black text-[#102C2B]">Visual Verification &amp; Anti-Fraud</h2>
          <p className="text-xs text-[#4B6363] font-medium leading-relaxed">
            SSIM structural similarity and dHash 64-bit perceptual fingerprinting compare BEFORE vs AFTER evidence photos to flag recycled photos or location mismatches before dispatches are marked resolved.
          </p>
        </div>
      </div>
    </div>
  );
}
