"use client";

import { useState, useRef } from "react";
import { MoveHorizontal } from "lucide-react";

interface BeforeAfterSliderProps {
  beforeImage: string;
  afterImage: string;
  beforeLabel?: string;
  afterLabel?: string;
}

export default function BeforeAfterSlider({
  beforeImage,
  afterImage,
  beforeLabel = "BEFORE (Report Photo)",
  afterLabel = "AFTER (Officer Fix)"
}: BeforeAfterSliderProps) {
  const [sliderPos, setSliderPos] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    let pos = (x / rect.width) * 100;
    if (pos < 0) pos = 0;
    if (pos > 100) pos = 100;
    setSliderPos(pos);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (e.touches.length > 0) {
      handleMove(e.touches[0].clientX);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      handleMove(e.clientX);
    }
  };

  return (
    <div
      ref={containerRef}
      onMouseDown={() => setIsDragging(true)}
      onMouseUp={() => setIsDragging(false)}
      onMouseLeave={() => setIsDragging(false)}
      onMouseMove={handleMouseMove}
      onTouchMove={handleTouchMove}
      className="relative w-full h-80 sm:h-96 rounded-3xl overflow-hidden shadow-xl border border-[#E7E9E4] select-none cursor-ew-resize group"
    >
      {/* After Image (Background) */}
      <img
        src={afterImage}
        alt="After Resolution"
        className="absolute inset-0 w-full h-full object-cover"
      />
      <span className="absolute top-4 right-4 bg-emerald-600/90 backdrop-blur-md text-white text-[10px] font-black uppercase px-3 py-1 rounded-full shadow-md z-10">
        {afterLabel}
      </span>

      {/* Before Image (Clipped Overlay) */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{ width: `${sliderPos}%` }}
      >
        <img
          src={beforeImage}
          alt="Before Report"
          className="absolute inset-0 w-full h-full object-cover"
          style={{ width: containerRef.current ? containerRef.current.offsetWidth : "100%" }}
        />
        <span className="absolute top-4 left-4 bg-red-600/90 backdrop-blur-md text-white text-[10px] font-black uppercase px-3 py-1 rounded-full shadow-md z-10 whitespace-nowrap">
          {beforeLabel}
        </span>
      </div>

      {/* Divider Drag Line & Handle */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-white shadow-2xl z-20"
        style={{ left: `${sliderPos}%` }}
      >
        <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-9 h-9 rounded-full bg-[#287C73] text-white shadow-2xl flex items-center justify-center border-2 border-white group-hover:scale-110 transition-transform teal-glow">
          <MoveHorizontal className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
}
