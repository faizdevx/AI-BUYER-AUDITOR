import React, { useEffect, useState } from 'react';
import type { SystemStatusStep } from '../types';
import { Architectural3D } from './Architectural3D';
import { RotateCw, Cpu, Database, Network, Search } from 'lucide-react';

interface AnalysisLoaderProps {
  onComplete: () => void;
  productTitle: string;
}

const STEPS: { step: SystemStatusStep; durationMs: number; desc: string; icon: React.FC<{ className?: string }> }[] = [
  { 
    step: 'PARSING PRODUCT', 
    durationMs: 2500, 
    desc: 'Extracting product token embeddings, attributes, and image features...', 
    icon: Cpu 
  },
  { 
    step: 'BUILDING PRODUCT VECTOR', 
    durationMs: 2500, 
    desc: 'Projecting product metadata into high-dimensional semantic latent space...', 
    icon: Database 
  },
  { 
    step: 'FINDING COMPETITORS', 
    durationMs: 2500, 
    desc: 'Indexing competitor catalogue schemas and price-to-feature utility vectors...', 
    icon: Search 
  },
  { 
    step: 'SIMULATING AI BUYER', 
    durationMs: 2500, 
    desc: 'Executing multi-agent procurement prompts across Claude, ChatGPT & Gemini...', 
    icon: Network 
  },
];

export const AnalysisLoader: React.FC<AnalysisLoaderProps> = ({ onComplete, productTitle }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progressPercent, setProgressPercent] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0.0);
  const [matrixLog, setMatrixLog] = useState<string[]>([]);

  useEffect(() => {
    const totalDuration = 10000;
    const startTime = Date.now();

    const interval = window.setInterval(() => {
      const now = Date.now();
      const elapsed = now - startTime;
      const pct = Math.min(100, Math.floor((elapsed / totalDuration) * 100));
      const secs = (elapsed / 1000).toFixed(1);

      setProgressPercent(pct);
      setElapsedSeconds(parseFloat(secs));

      const stepIdx = Math.min(STEPS.length - 1, Math.floor((elapsed / totalDuration) * STEPS.length));
      setCurrentStepIndex(stepIdx);

      if (elapsed >= totalDuration) {
        window.clearInterval(interval);
        setTimeout(() => {
          onComplete();
        }, 400);
      }
    }, 50);

    return () => window.clearInterval(interval);
  }, [onComplete]);

  useEffect(() => {
    const logTimer = window.setInterval(() => {
      const hex = Math.floor(Math.random() * 0xFFFFFF).toString(16).padStart(6, '0').toUpperCase();
      const val1 = (Math.random() * 0.99).toFixed(4);
      const val2 = (Math.random() * 0.99).toFixed(4);
      const val3 = (Math.random() * 0.99).toFixed(4);
      
      const newEntry = `0x${hex} :: [${val1}, ${val2}, ${val3}] :: LATENCY ${Math.floor(8 + Math.random() * 12)}ms`;
      
      setMatrixLog(prev => [newEntry, ...prev.slice(0, 7)]);
    }, 180);

    return () => window.clearInterval(logTimer);
  }, []);

  const currentStep = STEPS[currentStepIndex];

  return (
    <section className="relative w-full py-16 sm:py-24 bg-[#080C24] border-b border-navy-700/60 overflow-hidden min-h-[660px] flex items-center">
      <div className="absolute inset-0 bg-grid-tech opacity-30 pointer-events-none" />
      <div className="absolute -right-10 top-1/2 -translate-y-1/2 w-80 sm:w-[500px] h-[500px] opacity-40 pointer-events-none">
        <Architectural3D variant="dense" interactive={false} />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        
        <div className="flex items-center justify-between border-b border-navy-700/60 pb-3 mb-10 text-xs font-mono tracking-widest text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-crimson animate-ping" />
            <span className="text-crimson font-bold uppercase">SIMULATION IN PROGRESS</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-posterPink font-bold">{progressPercent}%</span>
            <span>[{elapsedSeconds.toFixed(1)}s / 10.0s]</span>
          </div>
        </div>

        {/* Large Editorial Headline: ANALYZING */}
        <div className="mb-8">
          <h2 className="text-posterPink font-black tracking-[-0.07em] uppercase text-6xl sm:text-8xl md:text-9xl lg:text-[10rem] leading-[0.76] select-none">
            ANALYZING
          </h2>
          <p className="text-slate-400 font-mono text-xs sm:text-sm tracking-wider uppercase mt-3">
            TARGET PRODUCT: <span className="text-white font-bold">{productTitle}</span>
          </p>
        </div>

        {/* Divider rules */}
        <div className="my-8">
          <div className="border-t border-crimson/40 border-b border-crimson/40 py-[2px]">
            <div className="border-t border-posterPink/20" />
          </div>
        </div>

        {/* Buffering rotating circular arrow & Current Step */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center pt-2">
          
          <div className="lg:col-span-6 flex items-center gap-6 p-6 sm:p-8 bg-[#0D1038] border border-navy-700 relative">
            <div className="absolute -top-[1px] -left-[1px] w-2 h-2 bg-crimson" />
            
            {/* Buffering Rotating Circular Arrow */}
            <div className="relative flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 border border-navy-700 flex items-center justify-center bg-navy-950">
              <RotateCw className="w-8 h-8 sm:w-10 sm:h-10 text-crimson animate-spin stroke-[2.5]" style={{ animationDuration: '2s' }} />
              <div className="absolute inset-1 border border-posterPink/30 animate-ping opacity-20" />
            </div>

            <div>
              <div className="flex items-center gap-2 text-[10px] font-mono tracking-widest text-slate-400 uppercase mb-1">
                <span>SYSTEM STATUS</span>
                <span className="text-crimson">//</span>
                <span>PHASE 0{currentStepIndex + 1} OF 04</span>
              </div>

              <div className="text-2xl sm:text-3xl font-black text-white uppercase tracking-tight font-sans">
                {currentStep.step}
              </div>

              <p className="text-xs font-mono text-slate-400 mt-1 max-w-sm">
                {currentStep.desc}
              </p>
            </div>
          </div>

          {/* Real-time Live Vector Stream Terminal */}
          <div className="lg:col-span-6 p-6 bg-navy-950 border border-navy-700 font-mono text-[11px] text-slate-400 relative">
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-navy-800 text-[10px] uppercase tracking-widest text-slate-400">
              <span>LIVE EMBEDDING PIPELINE</span>
              <span className="text-emerald-400">STREAMING TENSORS</span>
            </div>

            <div className="space-y-1.5 min-h-[140px] select-none">
              {matrixLog.map((line, i) => (
                <div key={i} className={`flex items-center justify-between ${i === 0 ? 'text-posterPink font-bold' : 'text-slate-400'}`}>
                  <span>{line}</span>
                  <span className="text-[9px] text-navy-500">TAG_{i}</span>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-3 border-t border-navy-800 flex items-center gap-3">
              <div className="flex-1 h-1.5 bg-navy-800 overflow-hidden">
                <div 
                  className="h-full bg-crimson transition-all duration-75"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <span className="text-[10px] text-slate-300 font-bold">{progressPercent}%</span>
            </div>
          </div>

        </div>

        {/* 4 Step Markers Progression */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-8">
          {STEPS.map((s, idx) => {
            const isDone = idx < currentStepIndex;
            const isCurrent = idx === currentStepIndex;
            return (
              <div 
                key={idx}
                className={`p-3 border font-mono text-[10px] uppercase transition-all ${
                  isDone 
                    ? 'border-emerald-500/50 bg-emerald-950/20 text-emerald-400' 
                    : isCurrent 
                      ? 'border-crimson bg-crimson/10 text-white font-bold ring-1 ring-crimson/50' 
                      : 'border-navy-800 bg-navy-950 text-slate-500'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span>0{idx + 1}</span>
                  <span>{isDone ? '✓ DONE' : isCurrent ? 'RUNNING' : 'QUEUED'}</span>
                </div>
                <div className="truncate">{s.step}</div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};