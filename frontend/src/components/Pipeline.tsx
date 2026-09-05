import React, { useState, useEffect } from 'react';
import type { PipelineStageInfo } from '../types';
import { Check, ArrowRight } from 'lucide-react';

interface PipelineProps {
  onAllCompleted: () => void;
}

const INITIAL_STAGES: PipelineStageInfo[] = [
  {
    id: 'parser',
    title: 'PRODUCT PARSER',
    subhead: 'MULTI-MODAL ATTRIBUTES EXTRACTED',
    status: 'pending',
  },
  {
    id: 'competition',
    title: 'COMPETITION ENGINE',
    subhead: 'CATALOGUE VECTOR INDEXING',
    status: 'pending',
  },
  {
    id: 'ai-buyer',
    title: 'AI BUYER SIMULATION',
    subhead: 'PROCURING REASONING RUNTIME',
    status: 'pending',
    models: ['Claude', 'ChatGPT', 'Gemini', 'Other AI Buyer'],
  },
  {
    id: 'audit-complete',
    title: 'AUDIT COMPLETE',
    subhead: 'PREFERENCE MATRIX COMPUTED',
    status: 'pending',
  },
];

export const Pipeline: React.FC<PipelineProps> = ({ onAllCompleted }) => {
  const [stages, setStages] = useState<PipelineStageInfo[]>(INITIAL_STAGES);

  useEffect(() => {
    const sequenceTimes = [500, 1200, 2000, 2800];
    const timerIds: number[] = [];

    sequenceTimes.forEach((time, index) => {
      const timer = window.setTimeout(() => {
        setStages(prev => prev.map((stage, i) => {
          if (i <= index) return { ...stage, status: 'completed' };
          return stage;
        }));

        if (index === sequenceTimes.length - 1) {
          window.setTimeout(() => {
            onAllCompleted();
          }, 800);
        }
      }, time);

      timerIds.push(timer);
    });

    return () => timerIds.forEach(window.clearTimeout);
  }, [onAllCompleted]);

  return (
    <section className="relative w-full py-12 sm:py-16 bg-[#0B0F2A] border-b border-navy-700/60 overflow-hidden">
      <div className="absolute inset-0 bg-grid-tech opacity-20 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        <div className="flex items-center justify-between pb-4 mb-6 border-b border-navy-700/60 text-xs font-mono tracking-widest text-slate-400">
          <div className="flex items-center gap-2">
            <span className="text-posterPink font-bold uppercase">[ 02 // PIPELINE PROGRESSION ]</span>
            <span className="text-navy-600">//</span>
            <span>LEFT → RIGHT EXECUTION</span>
          </div>
          <div className="hidden sm:block text-slate-500 font-bold">
            SEQUENTIAL INFERENCE PIPELINE
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-3xl sm:text-4xl font-black text-white uppercase tracking-tight font-sans">
            AI BUYER AUDIT PIPELINE
          </h2>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Real-time pipeline transition across parser, competitor indexing, and model evaluation nodes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
          
          {stages.map((stage, idx) => {
            const isCompleted = stage.status === 'completed';

            return (
              <div 
                key={stage.id} 
                className={`relative p-5 sm:p-6 bg-[#0D1038] border transition-all duration-300 flex flex-col justify-between min-h-[220px] ${
                  isCompleted 
                    ? 'border-posterPink/70 shadow-lg shadow-posterPink/5' 
                    : 'border-navy-700 opacity-60'
                }`}
              >
                <div 
                  className={`absolute top-0 left-0 right-0 h-1 transition-all ${
                    isCompleted ? 'bg-posterPink' : 'bg-navy-800'
                  }`} 
                />

                <div className="absolute -top-[1px] -left-[1px] w-1.5 h-1.5 bg-crimson" />
                <div className="absolute -bottom-[1px] -right-[1px] w-1.5 h-1.5 bg-posterPink" />

                <div>
                  <div className="flex items-center justify-between mb-3 text-[10px] font-mono tracking-wider">
                    <span className="text-slate-400 font-bold">NODE // 0{idx + 1}</span>
                    {isCompleted ? (
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-bold uppercase">
                        <Check className="w-3 h-3 stroke-[3]" /> COMPLETE
                      </span>
                    ) : (
                      <span className="text-slate-500 uppercase">PENDING</span>
                    )}
                  </div>

                  <h3 className="text-lg sm:text-xl font-black uppercase text-white tracking-tight leading-tight">
                    {stage.title}
                  </h3>

                  <p className="text-[11px] font-mono text-slate-400 mt-1">
                    {stage.subhead}
                  </p>
                </div>

                {stage.models && (
                  <div className="my-4 pt-3 border-t border-navy-800">
                    <div className="text-[9px] font-mono uppercase text-slate-400 tracking-widest mb-1.5 font-bold">
                      ACTIVE AI BUYER AGENTS:
                    </div>
                    <div className="grid grid-cols-2 gap-1.5">
                      {stage.models.map((m, mIdx) => (
                        <div 
                          key={mIdx}
                          className="px-2 py-1 bg-navy-950 border border-navy-700 text-[10px] font-mono text-posterPink tracking-wider flex items-center justify-between"
                        >
                          <span>{m}</span>
                          <span className="w-1 h-1 bg-crimson rounded-full" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {idx < stages.length - 1 && (
                  <div className="hidden md:block absolute -right-3.5 top-1/2 -translate-y-1/2 z-20 text-posterPink/70 bg-[#0D1038] p-0.5 border border-navy-700">
                    <ArrowRight className="w-3 h-3" />
                  </div>
                )}

                <div className="pt-3 border-t border-navy-800 flex items-center justify-between text-[9px] font-mono text-slate-400 uppercase">
                  <span>VECTOR: VALID</span>
                  <span className="text-posterPink font-bold">100% SYNCD</span>
                </div>

              </div>
            );
          })}

        </div>

      </div>
    </section>
  );
};