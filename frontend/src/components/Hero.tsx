import React from 'react';
import { Architectural3D } from './Architectural3D';

interface HeroProps {
  onScrollToInput: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onScrollToInput }) => {
  return (
    <section className="relative w-full pt-10 pb-12 sm:pt-16 sm:pb-20 border-b border-navy-700/60 overflow-hidden">
      {/* Background Architectural Grid & Subtle 3D Canvas */}
      <div className="absolute inset-0 bg-grid-tech opacity-40 pointer-events-none" />
      <div className="absolute right-0 top-0 w-full sm:w-2/5 h-full opacity-25 lg:opacity-45 pointer-events-none">
        <Architectural3D variant="hero" interactive={false} />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Hero Poster Headline: Deep Crimson Condensed Typography */}
        <div className="pt-2">
          <h1 className="text-crimson font-black tracking-[-0.055em] uppercase text-4xl sm:text-6xl md:text-7xl lg:text-[5.75rem] xl:text-[6.8rem] leading-[0.84] select-none">
            <span className="block transform scale-y-[1.12] origin-top">YOU’RE A MERCHANT,</span>
            <span className="block transform scale-y-[1.12] origin-top">HUH?!</span>
            <span className="block transform scale-y-[1.12] origin-top">AFRAID OF</span>
            <span className="block transform scale-y-[1.12] origin-top">AI BUYERS?</span>
          </h1>
        </div>

        {/* Dual Thin Horizontal Divider Rules (Reference Poster Style) */}
        <div className="my-8 sm:my-10">
          <div className="border-t border-posterPink/30 border-b border-posterPink/30 py-[2px]">
            <div className="border-t border-crimson/20" />
          </div>
        </div>

        {/* Second Headline: Crimson NOT + Enormous Pale Pink ANYMORE */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-end">
          <div className="lg:col-span-12">
            <div className="text-crimson font-black tracking-[-0.06em] text-5xl sm:text-7xl md:text-8xl lg:text-9xl leading-[0.78] uppercase mb-1 sm:mb-2 select-none">
              NOT
            </div>
            
            <div className="text-posterPink font-black tracking-[-0.075em] text-6xl sm:text-8xl md:text-[8rem] lg:text-[11.5rem] xl:text-[14rem] leading-[0.74] uppercase select-none overflow-visible">
              ANYMORE.
            </div>
          </div>
        </div>

        {/* Small Supporting Text */}
        <div className="mt-8 sm:mt-12 pt-6 border-t border-navy-700/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="max-w-xl">
            <p className="text-base sm:text-lg text-slate-200 font-medium tracking-tight">
              Make your product ready for the AI buyer.
            </p>
            <p className="text-xs sm:text-sm text-slate-400 font-mono mt-1 tracking-wide">
              Test how Claude, ChatGPT, Gemini, and autonomous procurement engines parse your product metadata, features, and pricing vectors against competing items.
            </p>
          </div>

          <button
            onClick={onScrollToInput}
            className="group flex items-center gap-3 px-6 py-3.5 bg-crimson hover:bg-posterPink text-white hover:text-navy-950 font-mono text-xs sm:text-sm font-bold tracking-widest uppercase transition-all duration-150 border border-crimson shadow-none active:translate-y-0.5"
          >
            <span>CONFIGURE AUDIT</span>
            <span className="group-hover:translate-x-1 transition-transform">↓</span>
          </button>
        </div>

      </div>
    </section>
  );
};