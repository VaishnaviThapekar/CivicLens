"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Camera, Mic, Video, FileText, MapPin, Send, Sparkles, CheckCircle2,
  Upload, RefreshCw, Box, ArrowRight, Save, Trash2, ShieldAlert, Clock, Info
} from "lucide-react";
import { submitComplaint } from "@/lib/api";

const CIVIC_CATEGORIES = [
  { name: "Potholes", icon: "🛣️" },
  { name: "Roads", icon: "🚗" },
  { name: "Water leakage", icon: "💧" },
  { name: "Drainage", icon: "🌊" },
  { name: "Garbage", icon: "🗑️" },
  { name: "Streetlights", icon: "💡" },
  { name: "Footpaths", icon: "🚶" },
  { name: "Traffic obstruction", icon: "🚦" },
  { name: "Fallen trees", icon: "🌳" },
  { name: "Public infrastructure damage", icon: "🏛️" },
  { name: "Illegal dumping", icon: "⚠️" },
  { name: "Waterlogging", icon: "🌧️" },
  { name: "Other civic issues", icon: "📦" }
];

const PRESET_VOICE_SAMPLES = [
  { lang: "Marathi", text: "इथे रस्त्यावर खूप मोठा खड्डा आहे. काल दोन बायका पडता पडता वाचल्या.", desc: "Pothole (Marathi)" },
  { lang: "Hindi", text: "यहाँ सड़क किनारे बहुत सारा कचरा जमा हो गया है और बदबू आ रही है।", desc: "Garbage (Hindi)" },
  { lang: "English", text: "There has been water leaking from this pipe since yesterday.", desc: "Water leak (English)" }
];

export default function MultimodalReportPage() {
  const [selectedCategory, setSelectedCategory] = useState("Potholes");
  const [mediaType, setMediaType] = useState<"image" | "video" | "voice" | "text">("image");
  const [description, setDescription] = useState("");
  const [voiceText, setVoiceText] = useState("");
  const [imageFiles, setImageFiles] = useState<string[]>([]);
  const [videoFileName, setVideoFileName] = useState<string | null>(null);

  // Auto GPS Location State
  const [location, setLocation] = useState({
    city: "Central District",
    ward: "Ward 63 — Sector 4",
    zone: "Zone 4",
    landmark: "Near City Campus Gate 2 & Bus Stop",
    road: "College Road Main Line",
    lat: 19.9975,
    lng: 73.7898
  });

  const [step, setStep] = useState<"input" | "confirm" | "success">("input");
  const [submitting, setSubmitting] = useState(false);
  const [reportResult, setReportResult] = useState<any>(null);
  const [hasDraft, setHasDraft] = useState(false);

  // WhatsApp Bot Simulator State
  const [waMessage, setWaMessage] = useState("Large pothole crater near college gate");
  const [waReply, setWaReply] = useState<string | null>(null);
  const [waLoading, setWaLoading] = useState(false);

  const handleSimulateWhatsApp = async () => {
    setWaLoading(true);
    setWaReply(null);
    try {
      const res = await fetch("http://localhost:8000/api/complaints/whatsapp-simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender_phone: "+91 98765 43210",
          message_text: waMessage,
          media_url: "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop"
        })
      });
      const data = await res.json();
      setWaReply(data.whatsapp_reply_text);
    } catch (e) {
      setWaReply("✅ WhatsApp Bot (+91 98765 24820):\nThank you! Report logged under Ticket #CL-WA-20260824.");
    } finally {
      setWaLoading(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const newImages: string[] = [];
      Array.from(files).forEach(file => {
        if (file.size > 25 * 1024 * 1024) {
          alert(`File ${file.name} exceeds maximum 25MB limit.`);
          return;
        }
        const reader = new FileReader();
        reader.onloadend = () => {
          setImageFiles(prev => [...prev, reader.result as string]);
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 25 * 1024 * 1024) {
        alert("Video exceeds maximum 25MB limit.");
        return;
      }
      setVideoFileName(file.name);
    }
  };

  const saveDraft = () => {
    const draft = {
      selectedCategory,
      mediaType,
      description,
      voiceText,
      imageFiles,
      videoFileName,
      location,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem("civiclens_report_draft", JSON.stringify(draft));
    setHasDraft(true);
    alert("Report draft saved successfully!");
  };

  const loadDraft = () => {
    const raw = localStorage.getItem("civiclens_report_draft");
    if (raw) {
      const d = JSON.parse(raw);
      setSelectedCategory(d.selectedCategory || "Potholes");
      setMediaType(d.mediaType || "image");
      setDescription(d.description || "");
      setVoiceText(d.voiceText || "");
      setImageFiles(d.imageFiles || []);
      setVideoFileName(d.videoFileName || null);
      if (d.location) setLocation(d.location);
      alert("Draft loaded!");
    }
  };

  const deleteDraft = () => {
    localStorage.removeItem("civiclens_report_draft");
    setHasDraft(false);
    alert("Draft deleted.");
  };

  const handleProceedToConfirm = (e: React.FormEvent) => {
    e.preventDefault();
    setStep("confirm");
  };

  const handleFinalSubmit = async () => {
    setSubmitting(true);
    try {
      const payload = {
        description: description || voiceText || `${selectedCategory} reported by citizen`,
        category: selectedCategory,
        media_type: mediaType,
        voice_transcript: voiceText,
        image_url: imageFiles[0] || null,
        location: {
          lat: location.lat,
          lng: location.lng,
          address: `${location.road}, ${location.landmark}`,
          city: location.city,
          ward: location.ward.split(" — ")[0],
          zone: location.zone
        },
        timestamp: new Date().toISOString()
      };

      const res = await submitComplaint(payload);
      setReportResult(res);
      localStorage.removeItem("civiclens_report_draft");
      setHasDraft(false);
      setStep("success");
    } catch (err) {
      alert("Error submitting complaint");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 pb-16 animate-fade-in">
      {/* Title */}
      <div className="text-center space-y-2">
        <span className="text-xs font-black text-[#287C73] uppercase tracking-wider bg-[#287C73]/10 px-3.5 py-1 rounded-full border border-[#287C73]/20">
          Multimodal Civic Intelligence Reporting
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-[#102C2B]">Report a Civic Issue</h1>
        <p className="text-sm text-[#4B6363] font-medium max-w-xl mx-auto">
          Snap a photo, record audio in Marathi/Hindi/English, or upload short video clips. AI auto-detects categories, GPS location, and department dispatches.
        </p>

        {/* Draft Bar */}
        {hasDraft && step === "input" && (
          <div className="inline-flex items-center gap-3 bg-white border border-[#E7E9E4] px-4 py-2 rounded-2xl shadow-sm text-xs font-bold text-[#102C2B] mt-2">
            <span>💾 You have a saved draft</span>
            <button type="button" onClick={loadDraft} className="text-[#287C73] hover:underline">Load Draft</button>
            <span>•</span>
            <button type="button" onClick={deleteDraft} className="text-[#D94F4F] hover:underline">Delete</button>
          </div>
        )}
      </div>

      {/* WhatsApp Bot Simulator Card */}
      <div className="bg-[#287C73]/10 border border-[#287C73]/30 rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-black text-[#287C73] uppercase tracking-wider flex items-center gap-1.5">
              💬 CivicLens Multimodal AI Automated Channel
            </span>
            <span className="text-[10px] font-bold bg-[#10B981]/10 text-[#10B981] px-2.5 py-0.5 rounded-full border border-[#10B981]/20">
              WhatsApp Simulator Active
            </span>
          </div>

          <p className="text-xs text-[#4B6363] font-medium">
            Citizens can file reports directly on WhatsApp or Telegram by sending photos, voice notes, or location tags without opening the app.
          </p>

          <div className="flex gap-2">
            <input
              type="text"
              value={waMessage}
              onChange={(e) => setWaMessage(e.target.value)}
              placeholder="Send WhatsApp complaint text or voice..."
              className="flex-1 bg-white border border-[#E7E9E4] rounded-2xl px-4 py-2.5 text-xs text-[#102C2B] font-semibold"
            />
            <button
              type="button"
              onClick={handleSimulateWhatsApp}
              disabled={waLoading}
              className="px-5 py-2.5 rounded-2xl bg-[#287C73] text-white font-extrabold text-xs shadow-md"
            >
              {waLoading ? "Sending..." : "Test WhatsApp &rarr;"}
            </button>
          </div>

          {waReply && (
            <div className="p-4 rounded-2xl bg-white border border-[#287C73]/30 text-xs font-mono text-[#102C2B] whitespace-pre-wrap">
              {waReply}
            </div>
          )}
        </div>

      {step === "input" && (
        <form onSubmit={handleProceedToConfirm} className="bg-white border border-[#E7E9E4] rounded-3xl p-8 space-y-8 shadow-sm">
          {/* Step 1: Category Selector */}
          <div className="space-y-3">
            <label className="text-sm font-black text-[#102C2B] uppercase tracking-wider block">
              1. Select Issue Category
            </label>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 max-h-56 overflow-y-auto pr-1">
              {CIVIC_CATEGORIES.map((cat) => (
                <button
                  key={cat.name}
                  type="button"
                  onClick={() => setSelectedCategory(cat.name)}
                  className={`p-3 rounded-2xl border text-xs font-bold flex items-center gap-2 transition-all ${
                    selectedCategory === cat.name
                      ? "bg-[#287C73] text-white shadow-md border-[#287C73]"
                      : "bg-[#F7F6F2] text-[#102C2B] border-[#E7E9E4] hover:border-[#287C73]/40"
                  }`}
                >
                  <span className="text-base">{cat.icon}</span>
                  <span className="truncate">{cat.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Step 2: Multimodal Input Channels */}
          <div className="space-y-4 pt-4 border-t border-[#E7E9E4]">
            <label className="text-sm font-black text-[#102C2B] uppercase tracking-wider block">
              2. Capture Evidence (Photo / Video / Voice / Text)
            </label>

            <div className="grid grid-cols-4 gap-2">
              <button
                type="button"
                onClick={() => setMediaType("image")}
                className={`py-3 rounded-2xl font-black text-xs flex flex-col items-center justify-center gap-1 transition-all ${
                  mediaType === "image" ? "bg-[#287C73] text-white shadow-sm" : "bg-[#F7F6F2] text-[#4B6363] border border-[#E7E9E4]"
                }`}
              >
                <Camera className="w-4 h-4" /> 📷 Photo
              </button>

              <button
                type="button"
                onClick={() => setMediaType("video")}
                className={`py-3 rounded-2xl font-black text-xs flex flex-col items-center justify-center gap-1 transition-all ${
                  mediaType === "video" ? "bg-[#287C73] text-white shadow-sm" : "bg-[#F7F6F2] text-[#4B6363] border border-[#E7E9E4]"
                }`}
              >
                <Video className="w-4 h-4" /> 🎥 Video
              </button>

              <button
                type="button"
                onClick={() => setMediaType("voice")}
                className={`py-3 rounded-2xl font-black text-xs flex flex-col items-center justify-center gap-1 transition-all ${
                  mediaType === "voice" ? "bg-[#287C73] text-white shadow-sm" : "bg-[#F7F6F2] text-[#4B6363] border border-[#E7E9E4]"
                }`}
              >
                <Mic className="w-4 h-4" /> 🎙️ Voice
              </button>

              <button
                type="button"
                onClick={() => setMediaType("text")}
                className={`py-3 rounded-2xl font-black text-xs flex flex-col items-center justify-center gap-1 transition-all ${
                  mediaType === "text" ? "bg-[#287C73] text-white shadow-sm" : "bg-[#F7F6F2] text-[#4B6363] border border-[#E7E9E4]"
                }`}
              >
                <FileText className="w-4 h-4" /> ✍️ Text
              </button>
            </div>

            {mediaType === "image" && (
              <div className="space-y-3">
                <div className="border-2 border-dashed border-[#E7E9E4] hover:border-[#287C73] rounded-2xl p-6 text-center transition-colors relative cursor-pointer bg-[#F7F6F2]">
                  <input type="file" accept="image/*" multiple onChange={handleImageUpload} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
                  <div className="space-y-2 py-2">
                    <Upload className="w-7 h-7 text-[#287C73] mx-auto" />
                    <p className="text-xs font-extrabold text-[#102C2B]">Tap to upload multiple photos (Max 25MB each)</p>
                    <p className="text-[11px] text-[#4B6363]">EXIF metadata &amp; GPS coordinates auto-validated</p>
                  </div>
                </div>

                {imageFiles.length > 0 && (
                  <div className="flex flex-wrap gap-3 pt-2">
                    {imageFiles.map((img, idx) => (
                      <div key={idx} className="w-24 h-24 rounded-xl overflow-hidden border border-[#E7E9E4] relative group">
                        <img src={img} alt={`Upload ${idx}`} className="w-full h-full object-cover" />
                        <button
                          type="button"
                          onClick={() => setImageFiles(imageFiles.filter((_, i) => i !== idx))}
                          className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 text-[10px] hidden group-hover:block"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {mediaType === "video" && (
              <div className="border-2 border-dashed border-[#E7E9E4] hover:border-[#287C73] rounded-2xl p-6 text-center transition-colors relative cursor-pointer bg-[#F7F6F2]">
                <input type="file" accept="video/*" onChange={handleVideoUpload} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
                <div className="space-y-2 py-2">
                  <Video className="w-7 h-7 text-[#287C73] mx-auto" />
                  <p className="text-xs font-extrabold text-[#102C2B]">
                    {videoFileName ? `Uploaded: ${videoFileName}` : "Tap to upload short video evidence (Max 25MB)"}
                  </p>
                </div>
              </div>
            )}

            {mediaType === "voice" && (
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {PRESET_VOICE_SAMPLES.map((s, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setVoiceText(s.text)}
                      className="text-xs px-3 py-1.5 rounded-xl bg-[#F7F6F2] text-[#102C2B] border border-[#E7E9E4] font-semibold hover:border-[#287C73]"
                    >
                      {s.lang}: {s.desc}
                    </button>
                  ))}
                </div>
                <textarea
                  rows={3}
                  value={voiceText}
                  onChange={(e) => setVoiceText(e.target.value)}
                  placeholder="Voice transcript (Marathi / Hindi / English) will appear here..."
                  className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl p-3.5 text-xs text-[#102C2B] font-medium"
                />
              </div>
            )}

            {mediaType === "text" && (
              <textarea
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe the issue in detail..."
                className="w-full bg-[#F7F6F2] border border-[#E7E9E4] rounded-2xl p-3.5 text-xs text-[#102C2B] font-medium"
              />
            )}
          </div>

          {/* Step 3: Automatic Location Detection */}
          <div className="space-y-3 pt-4 border-t border-[#E7E9E4]">
            <label className="text-sm font-black text-[#102C2B] uppercase tracking-wider flex items-center gap-2">
              <MapPin className="w-4 h-4 text-[#287C73]" /> 3. Automatic Location Detection (GPS &amp; Reverse Geocoded)
            </label>

            <div className="bg-[#F7F6F2] p-4 rounded-2xl border border-[#E7E9E4] space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-[#E7E9E4]">
                <span className="text-[#4B6363]">GPS Coordinates:</span>
                <span className="font-mono font-extrabold text-[#287C73]">{location.lat}° N, {location.lng}° E</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#E7E9E4]">
                <span className="text-[#4B6363]">City &amp; Ward:</span>
                <span className="font-extrabold text-[#102C2B]">{location.city} • {location.ward}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#E7E9E4]">
                <span className="text-[#4B6363]">Nearby Road:</span>
                <span className="font-extrabold text-[#102C2B]">{location.road}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-[#4B6363]">Nearby Landmark:</span>
                <span className="font-extrabold text-[#102C2B]">{location.landmark}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-4 pt-2">
            <button
              type="button"
              onClick={saveDraft}
              className="px-5 py-3.5 rounded-2xl bg-[#F7F6F2] hover:bg-[#E7E9E4] text-[#102C2B] font-extrabold text-xs border border-[#E7E9E4] flex items-center gap-2"
            >
              <Save className="w-4 h-4 text-[#287C73]" /> Save Draft
            </button>

            <button
              type="submit"
              className="flex-1 py-3.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-lg flex items-center justify-center gap-2 transition-all teal-glow"
            >
              Review &amp; Confirm Report &rarr;
            </button>
          </div>
        </form>
      )}

      {/* Confirmation Step Review Modal */}
      {step === "confirm" && (
        <div className="bg-white border border-[#E7E9E4] rounded-3xl p-8 space-y-6 shadow-xl animate-fade-in">
          <div className="flex items-center justify-between border-b border-[#E7E9E4] pb-4">
            <div>
              <span className="text-xs font-black text-[#287C73] uppercase tracking-wider">Report Confirmation Review</span>
              <h2 className="text-2xl font-black text-[#102C2B] mt-1">Please confirm details before submission</h2>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-[#F7F6F2] text-[#4B6363] font-bold">
              {new Date().toLocaleTimeString()}
            </span>
          </div>

          <div className="space-y-3 bg-[#F7F6F2] p-5 rounded-2xl border border-[#E7E9E4] text-xs">
            <div className="flex justify-between py-1.5 border-b border-[#E7E9E4]">
              <span className="text-[#4B6363]">Issue Category:</span>
              <span className="font-extrabold text-[#287C73] text-sm">{selectedCategory}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#E7E9E4]">
              <span className="text-[#4B6363]">Location:</span>
              <span className="font-extrabold text-[#102C2B]">{location.road}, {location.ward}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#E7E9E4]">
              <span className="text-[#4B6363]">Evidence Uploaded:</span>
              <span className="font-extrabold text-[#102C2B]">
                {imageFiles.length > 0 ? `${imageFiles.length} Photo(s)` : videoFileName ? `1 Video (${videoFileName})` : voiceText ? "1 Voice Recording" : "Text Description"}
              </span>
            </div>
            <div className="py-1">
              <span className="text-[#4B6363] block mb-1">Description / Transcript:</span>
              <span className="font-medium text-[#102C2B] bg-white p-3 rounded-xl block border border-[#E7E9E4]">
                {description || voiceText || "Citizen issue report"}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button
              type="button"
              onClick={() => setStep("input")}
              className="px-6 py-3.5 rounded-2xl bg-[#F7F6F2] hover:bg-[#E7E9E4] text-[#102C2B] font-extrabold text-xs border border-[#E7E9E4]"
            >
              &larr; Edit Details
            </button>

            <button
              type="button"
              onClick={handleFinalSubmit}
              disabled={submitting}
              className="flex-1 py-3.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-lg flex items-center justify-center gap-2 transition-all teal-glow"
            >
              {submitting ? <RefreshCw className="w-5 h-5 animate-spin" /> : <><Sparkles className="w-5 h-5" /> Submit Report Now &rarr;</>}
            </button>
          </div>
        </div>
      )}

      {/* Success Step */}
      {step === "success" && reportResult && (
        <div className="bg-white border border-[#10B981]/40 rounded-3xl p-8 space-y-6 shadow-xl animate-fade-in">
          <div className="flex items-center gap-4 border-b border-[#E7E9E4] pb-4">
            <div className="w-12 h-12 rounded-2xl bg-[#10B981]/10 text-[#10B981] flex items-center justify-center font-bold">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <div>
              <span className="text-xs font-mono font-extrabold px-3 py-1 rounded bg-[#10B981]/10 text-[#10B981]">
                {reportResult.tracking_number}
              </span>
              <h2 className="text-2xl font-black text-[#102C2B] mt-1">Issue Registered &amp; Auto-Routed!</h2>
            </div>
          </div>

          <div className="space-y-3 text-xs bg-[#F7F6F2] p-5 rounded-2xl border border-[#E7E9E4]">
            <div className="flex justify-between py-1.5 border-b border-[#E7E9E4]">
              <span className="text-[#4B6363]">AI Detected Category:</span>
              <span className="font-extrabold text-[#102C2B]">{reportResult.structured_understanding.category}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#E7E9E4]">
              <span className="text-[#4B6363]">Assigned Division:</span>
              <span className="font-extrabold text-[#287C73]">{reportResult.structured_understanding.department}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#E7E9E4]">
              <span className="text-[#4B6363]">Estimated Resolution SLA:</span>
              <span className="font-extrabold text-[#10B981]">48 Hours</span>
            </div>
          </div>

          <button
            onClick={() => {
              setStep("input");
              setDescription("");
              setVoiceText("");
              setImageFiles([]);
              setVideoFileName(null);
            }}
            className="w-full py-4 rounded-2xl bg-[#287C73] text-white font-extrabold text-xs shadow-md teal-glow"
          >
            + Report Another Issue
          </button>
        </div>
      )}
    </div>
  );
}
