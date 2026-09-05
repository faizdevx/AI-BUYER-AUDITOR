import React from 'react';

interface HeaderProps {
  onReset: () => void;
  isAnalyzing: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onReset, isAnalyzing }) => {
  return (
    <header className="w-full border-b border-navy-700/60 bg-[#0D1038]/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        
        {/* Left: CURSP */}
        <div className="flex items-center gap-3">
          <button 
            onClick={onReset}
            className="text-left group flex items-center gap-2 focus:outline-none"
            title="Reset simulation to Home"
          >
            <span className="text-xl sm:text-2xl font-black tracking-tighter text-white group-hover:text-crimson transition-colors font-sans">
              CURSP
            </span>
            <span className="inline-block w-1.5 h-1.5 bg-crimson animate-pulse rounded-none" />
          </button>
          
          <div className="hidden md:flex items-center gap-2 pl-3 border-l border-navy-700 text-[10px] font-mono tracking-widest text-slate-400 uppercase">
            <span>SYS.VER 2.6.4</span>
            <span>//</span>
            <span className="text-posterPink font-bold">AI BUYER AUDIT SIMULATION</span>
          </div>
        </div>

        {/* Right: Understated Editorial Navigation */}
        <nav className="flex items-center gap-5 sm:gap-8 text-[11px] sm:text-xs font-mono tracking-widest text-slate-300">
          <a 
            href="#work" 
            onClick={(e) => { 
              e.preventDefault(); 
              const el = document.getElementById('product-input-section');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="hover:text-posterPink transition-colors uppercase py-1"
          >
            WORK
          </a>
          <a 
            href="#how-it-works" 
            onClick={(e) => { 
              e.preventDefault(); 
              const el = document.getElementById('product-input-section');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="hover:text-posterPink transition-colors uppercase py-1"
          >
            HOW IT WORKS
          </a>
          <a 
            href="#about" 
            onClick={(e) => { 
              e.preventDefault(); 
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
            className="hover:text-posterPink transition-colors uppercase py-1"
          >
            ABOUT
          </a>

          {isAnalyzing && (
            <div className="hidden sm:flex items-center gap-1.5 px-2 py-0.5 bg-crimson/20 border border-crimson/40 text-crimson text-[10px] font-mono uppercase">
              <span className="w-1.5 h-1.5 bg-crimson animate-ping" />
              <span>SIMULATING</span>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
};