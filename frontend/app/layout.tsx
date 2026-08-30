import "./globals.css";
import Link from "next/link";
import { MapPin, Camera, Compass } from "lucide-react";
import VoiceAssistantWidget from "@/components/VoiceAssistantWidget";
import LiveActivityTicker from "@/components/LiveActivityTicker";

export const metadata = {
  title: "CivicLens — See your city. Make it better.",
  description: "AI-powered civic intelligence platform that turns citizen reports into verified, prioritized civic action.",
  icons: {
    icon: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#FFFFFF] dark:bg-[#0F141C] text-[#102C2B] dark:text-[#F8FAFC] min-h-screen flex flex-col antialiased transition-colors duration-300">
        {/* Floating Multilingual Voice Assistant Widget */}
        <VoiceAssistantWidget />

        {/* Live Civic Activity Ticker */}
        <LiveActivityTicker />

        {/* Streamlined, Perfectly Aligned Header Navbar */}
        <header className="sticky top-0 z-50 bg-[#FFFFFF]/95 dark:bg-[#0F141C]/95 backdrop-blur-md border-b border-[#E7E9E4] dark:border-[#2D3B54]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            {/* Left: Brand Identity & City Selector */}
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-3 group">
                <div className="w-10 h-10 rounded-2xl bg-[#287C73] text-white flex items-center justify-center font-black text-xl shadow-md group-hover:scale-105 transition-transform teal-glow">
                  <span>C</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-black tracking-tight text-[#102C2B] dark:text-white">CivicLens</span>
                  <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-[#287C73]/10 text-[#287C73] border border-[#287C73]/20 uppercase tracking-wider">
                    ✦ CIVIC AI
                  </span>
                </div>
              </Link>

              {/* City Grid Selector Pill */}
              <div className="hidden xl:flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-white dark:bg-[#161E2E] border border-[#E7E9E4] dark:border-[#2D3B54] text-xs font-bold text-[#102C2B] dark:text-white shadow-sm cursor-pointer">
                <MapPin className="w-3.5 h-3.5 text-[#287C73]" />
                <span>Central District</span>
                <span className="text-[10px] text-[#4B6363] dark:text-[#94A3B8] font-medium">• Live Grid</span>
              </div>
            </div>

            {/* Center: Main Navigation */}
            <nav className="hidden md:flex items-center space-x-7 text-xs font-extrabold text-[#4B6363] dark:text-[#94A3B8]">
              <Link href="/explore" className="hover:text-[#287C73] transition-colors flex items-center gap-1.5 py-1">
                <Compass className="w-3.5 h-3.5 text-[#287C73]" /> Explore
              </Link>
              <Link href="/map" className="hover:text-[#287C73] transition-colors flex items-center gap-1.5 py-1">
                <MapPin className="w-3.5 h-3.5 text-[#287C73]" /> Live Map
              </Link>
              <Link href="/how-it-works" className="hover:text-[#287C73] transition-colors py-1">
                How It Works
              </Link>
              <Link href="/impact" className="hover:text-[#287C73] transition-colors py-1">
                Impact
              </Link>
              <Link href="/contractors" className="hover:text-[#287C73] transition-colors py-1">
                Contractors
              </Link>
              <Link href="/citizen" className="hover:text-[#287C73] transition-colors py-1">
                My Reports
              </Link>
            </nav>

            {/* Right: Clean Action Buttons */}
            <div className="flex items-center space-x-3">
              <Link
                href="/officer"
                className="hidden sm:inline-flex items-center gap-1 text-xs font-extrabold px-4 py-2.5 rounded-2xl border border-[#E7E9E4] dark:border-[#2D3B54] bg-white dark:bg-[#161E2E] text-[#102C2B] dark:text-white hover:border-[#287C73] transition-all shadow-sm"
              >
                Authority Portal &rarr;
              </Link>

              <Link
                href="/report"
                className="px-5 py-2.5 rounded-2xl bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-md shadow-[#287C73]/20 flex items-center gap-1.5 transition-all hover:scale-[1.03] teal-glow"
              >
                <Camera className="w-3.5 h-3.5" /> 📸 Report Issue
              </Link>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-[#E7E9E4] dark:border-[#2D3B54] bg-[#FFFFFF] dark:bg-[#161E2E] py-10 mt-16 text-xs text-[#4B6363] dark:text-[#94A3B8]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-1 text-center md:text-left">
              <div className="flex items-center justify-center md:justify-start space-x-2">
                <div className="w-6 h-6 rounded-lg bg-[#287C73] text-white flex items-center justify-center font-black text-xs">C</div>
                <span className="font-extrabold text-base text-[#102C2B] dark:text-white">CivicLens</span>
              </div>
              <p className="text-xs text-[#4B6363] dark:text-[#94A3B8]">See your city. Make it better.</p>
            </div>

            <div className="flex flex-wrap justify-center gap-6 font-semibold text-xs text-[#4B6363] dark:text-[#94A3B8]">
              <Link href="/explore" className="hover:text-[#287C73]">Explore City</Link>
              <Link href="/how-it-works" className="hover:text-[#287C73]">AI Pipeline</Link>
              <Link href="/impact" className="hover:text-[#287C73]">Impact &amp; Governance</Link>
              <Link href="/report" className="hover:text-[#287C73]">Report Issue</Link>
              <Link href="/officer" className="hover:text-[#287C73]">Municipal Portal</Link>
            </div>

            <div className="text-center md:text-right text-[11px] text-[#4B6363] dark:text-[#94A3B8]">
              &copy; 2026 CivicLens. AI-Powered Civic Intelligence &amp; Resolution Verification Platform.
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
