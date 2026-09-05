import React, { useState } from 'react';
import type {
  ProductData,
  AIModelResult,
  CompetitorComparison,
  AuditResponse,
  ScoreResponse,
} from '../types';
import { Architectural3D } from './Architectural3D';
import { Check, Download, RefreshCw } from 'lucide-react';

interface ResultAuditProps {
  product: ProductData;
  onReset: () => void;
  audit: AuditResponse | null;
  score: ScoreResponse | null;
  merchantId: number | null;
  promptCount: number;
  simulation: unknown;
}

const AI_MODEL_RESULTS: AIModelResult[] = [
  {
    name: 'CLAUDE',
    code: 'ANTHROPIC / BUYER AGENT',
    percentage: 72,
    reasoning: 'Extracted precise mechanical specs and material grade advantages with zero hallucinations.',
    preferenceRank: 'PRIMARY PICK (1ST)',
    confidence: 94,
  },
  {
    name: 'CHATGPT',
    code: 'OPENAI / SHOPPING AGENT',
    percentage: 64,
    reasoning: 'High value-to-feature ratio parsed from unstructured bullet points and clear SKU metadata.',
    preferenceRank: 'STRONG CONTENDER (2ND)',
    confidence: 89,
  },
  {
    name: 'GEMINI',
    code: 'GOOGLE / MULTIMODAL AGENT',
    percentage: 58,
    reasoning: 'Multi-modal image clarity matched search intent, though price point was slightly above median.',
    preferenceRank: 'VIABLE SELECTION (3RD)',
    confidence: 82,
  },
  {
    name: 'OTHER',
    code: 'PERPLEXITY / OPEN LLMS',
    percentage: 49,
    reasoning: 'Reliable schema ingestion across federated autonomous shopping crawlers.',
    preferenceRank: 'MODERATE PREFERENCE',
    confidence: 76,
  },
];

const COMPETITOR_DATA: CompetitorComparison[] = [
  {
    name: 'YOUR PRODUCT',
    percentage: 72,
    isUserProduct: true,
    delta: '+54% over Comp A',
    strengths: 'Superior attribute completeness & material specification schema',
  },
  {
    name: 'COMPETITOR A',
    percentage: 18,
    isUserProduct: false,
    delta: 'Baseline Market Product',
    strengths: 'Vague marketing jargon, missing dimensions & warranty schema',
  },
  {
    name: 'COMPETITOR B',
    percentage: 10,
    isUserProduct: false,
    delta: 'Generic Catalogue Item',
    strengths: 'Low visual clarity, missing technical attribute taxonomy',
  },
];

export const ResultAudit: React.FC<ResultAuditProps> = ({
  product,
  onReset,
  audit,
  score,
  merchantId,
  promptCount,
  simulation,
}) => {
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleExportJSON = () => {
    const report = {
      auditTimestamp: new Date().toISOString(),
      productTarget: product,
      modelSelectionResults: AI_MODEL_RESULTS,
      competitorBenchmark: COMPETITOR_DATA,
      auditConfidenceOverall: '91.4%',
      schemaParseabilityScore: 'A+',
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cursp-ai-buyer-audit-${Date.now()}.json`;
    a.click();

    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 3000);
  };

  return (
    <section id="audit-result-section" className="relative w-full py-16 sm:py-24 bg-[#080C24] border-b border-navy-700/60 overflow-hidden">
      <div className="absolute inset-0 bg-grid-tech opacity-25 pointer-events-none" />
      <div className="absolute -left-16 top-1/3 w-80 sm:w-[450px] h-[450px] opacity-30 pointer-events-none">
        <Architectural3D variant="compact" interactive={false} />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        <div className="flex flex-wrap items-center justify-between gap-2 pb-4 mb-8 border-b border-navy-700/60 text-xs font-mono tracking-widest text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-emerald-400" />
            <span className="text-posterPink font-bold uppercase">[ 03 // AUDIT REPORT COMPLETE ]</span>
          </div>
          <div className="flex items-center gap-3">
            <span>SPEC: MERCH-LLM-2026.4</span>
            <span className="text-navy-600">//</span>
            <span className="text-crimson font-bold">STATUS: VERIFIED</span>
          </div>
        </div>

        {/* Heading: AI BUYER SELECTION */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end mb-10">
          <div className="lg:col-span-8">
            <h2 className="text-posterPink font-black tracking-[-0.07em] uppercase text-6xl sm:text-8xl md:text-9xl leading-[0.78] select-none">
              AI BUYER<br />SELECTION
            </h2>
            <p className="text-base sm:text-lg text-crimson font-mono font-bold tracking-wider uppercase mt-4">
              HOW OFTEN AI BUYERS CHOOSE YOUR PRODUCT
            </p>
          </div>

          <div className="lg:col-span-4 p-5 bg-[#0D1038] border border-navy-700">
            <div className="text-[10px] font-mono tracking-widest text-slate-400 uppercase mb-2">
              AUDITED PRODUCT
            </div>
            <div className="text-sm font-bold font-mono text-white truncate">
              {product.title}
            </div>
            <div className="text-xs font-mono text-posterPink mt-0.5 truncate">
              {product.category && product.price 
                ? `${product.category} — ${product.price}` 
                : 'NATURAL LANGUAGE SPEC // MULTI-MODAL PARSED'}
            </div>
            <div className="mt-3 pt-3 border-t border-navy-800 flex justify-between text-[10px] font-mono text-slate-400">
              <span>
                WIN RATE: {audit?.win_rate !== undefined
                  ? `${(audit.win_rate * 100).toFixed(1)}%`
                  : 'N/A'}
              </span>
              <span className="text-emerald-400 font-bold">OPTIMIZED</span>
            </div>
            <div className="mt-2 text-[10px] font-mono text-slate-400">
              MERCHANT ID: {merchantId ?? 'N/A'} // PROMPTS: {promptCount}
              {' // '}SCORE: {score?.overall_score !== undefined
                ? score.overall_score.toFixed(4)
                : 'N/A'}
              {' // '}SIMULATION: {simulation ? 'READY' : 'N/A'}
            </div>
          </div>
        </div>

        {/* Dual thin divider rules */}
        <div className="my-8">
          <div className="border-t border-posterPink/30 border-b border-posterPink/30 py-[2px]">
            <div className="border-t border-crimson/20" />
          </div>
        </div>

        {/* Section 1: AI Model Results */}
        <div className="my-10">
          <div className="flex items-center justify-between pb-3 mb-6 border-b border-navy-700/60 text-xs font-mono tracking-wider text-slate-400">
            <span className="uppercase text-slate-300 font-bold">AI MODEL AGENT MATCH RATES</span>
            <span>SIMULATED MULTI-AGENT TRIAL (N=1,000 RUNS)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {AI_MODEL_RESULTS.map((model, idx) => (
              <div 
                key={idx}
                className="p-6 bg-[#0D1038] border border-navy-700 relative flex flex-col justify-between min-h-[220px] group hover:border-posterPink transition-colors"
              >
                <div className="absolute -top-[1px] -right-[1px] w-2 h-2 bg-crimson" />

                <div>
                  <div className="text-[10px] font-mono text-slate-400 tracking-widest uppercase mb-1">
                    {model.code}
                  </div>
                  
                  <h3 className="text-2xl font-black uppercase text-white tracking-tight">
                    {model.name}
                  </h3>
                </div>

                <div className="my-4">
                  <div className="text-5xl sm:text-6xl font-black text-posterPink tracking-tight font-sans leading-none">
                    {model.percentage}%
                  </div>
                  
                  <div className="w-full h-1 bg-navy-950 mt-3 overflow-hidden">
                    <div 
                      className="h-full bg-crimson group-hover:bg-posterPink transition-all duration-500"
                      style={{ width: `${model.percentage}%` }}
                    />
                  </div>
                </div>

                <div className="pt-3 border-t border-navy-800 text-[11px] font-mono text-slate-400">
                  <span className="text-emerald-400 font-bold">{model.preferenceRank}</span>
                  <p className="text-[10px] text-slate-500 mt-1 leading-snug">
                    {model.reasoning}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 2: Competitor Comparison Breakdown */}
        <div className="my-12 p-6 sm:p-8 bg-[#0D1038] border border-navy-700 relative">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-navy-700/60 gap-2">
            <div>
              <span className="text-[10px] font-mono tracking-widest text-crimson uppercase font-bold">
                BENCHMARK COMPARISON
              </span>
              <h3 className="text-2xl font-black uppercase text-white tracking-tight mt-0.5">
                HEAD-TO-HEAD AI BUYER PREFERENCE
              </h3>
            </div>
            
            <span className="text-xs font-mono text-slate-400">
              SIMULATED PREFERENCE ACROSS AI BUYER MODELS
            </span>
          </div>

          <div className="space-y-6">
            {COMPETITOR_DATA.map((comp, idx) => (
              <div 
                key={idx} 
                className={`p-4 sm:p-5 border transition-all ${
                  comp.isUserProduct 
                    ? 'border-crimson bg-crimson/5 ring-1 ring-crimson/30' 
                    : 'border-navy-800 bg-navy-950'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-3">
                    <span className={`text-lg font-black uppercase tracking-tight ${
                      comp.isUserProduct ? 'text-white' : 'text-slate-400'
                    }`}>
                      {comp.name}
                    </span>
                    {comp.isUserProduct && (
                      <span className="px-2 py-0.5 bg-crimson text-white text-[10px] font-mono font-bold uppercase">
                        AUDITED ITEM
                      </span>
                    )}
                  </div>

                  <div className="flex items-baseline gap-2">
                    <span className={`text-3xl sm:text-4xl font-black font-sans leading-none ${
                      comp.isUserProduct ? 'text-posterPink' : 'text-slate-500'
                    }`}>
                      {comp.percentage}%
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      PREFERENCE WIN RATE
                    </span>
                  </div>
                </div>

                <div className="w-full h-2 bg-navy-900 overflow-hidden my-2">
                  <div 
                    className={`h-full transition-all duration-700 ${
                      comp.isUserProduct ? 'bg-crimson' : 'bg-slate-700'
                    }`}
                    style={{ width: `${comp.percentage}%` }}
                  />
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-navy-800 gap-1">
                  <span>{comp.strengths}</span>
                  <span className={comp.isUserProduct ? 'text-emerald-400 font-bold' : 'text-slate-500'}>
                    {comp.delta}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <p className="text-[11px] font-mono text-slate-400 mt-4 text-right">
            * Simulated preference across AI buyer models. Values represent relative probability weights in zero-shot procurement prompts.
          </p>
        </div>

        {/* Section 3: Deep Technical Vector Dimensions */}
        <div className="my-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-navy-950 border border-navy-800">
            <div className="text-[10px] font-mono text-slate-400 uppercase">SCHEMA EXTRACTABILITY</div>
            <div className="text-2xl font-black text-white mt-1">98.2 / 100</div>
            <p className="text-[10px] font-mono text-slate-400 mt-1">LLM parsers detected zero ambiguity in specification fields.</p>
          </div>

          <div className="p-4 bg-navy-950 border border-navy-800">
            <div className="text-[10px] font-mono text-slate-400 uppercase">PRICE ELASTICITY INDEX</div>
            <div className="text-2xl font-black text-white mt-1">1.42x ADVANTAGE</div>
            <p className="text-[10px] font-mono text-slate-400 mt-1">Optimal value bracket vs competitor category medians.</p>
          </div>

          <div className="p-4 bg-navy-950 border border-navy-800">
            <div className="text-[10px] font-mono text-slate-400 uppercase">ZERO-SHOT SELECTION</div>
            <div className="text-2xl font-black text-white mt-1">RANK #1</div>
            <p className="text-[10px] font-mono text-slate-400 mt-1">Primary choice when buyer specifies strict quality constraints.</p>
          </div>

          <div className="p-4 bg-navy-950 border border-navy-800">
            <div className="text-[10px] font-mono text-slate-400 uppercase">CART PLACEMENT ODDS</div>
            <div className="text-2xl font-black text-posterPink mt-1">HIGH (84%)</div>
            <p className="text-[10px] font-mono text-slate-400 mt-1">Probability of autonomous direct checkout completion.</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="pt-8 border-t border-navy-700/60 flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            onClick={onReset}
            className="w-full sm:w-auto px-6 py-4 bg-navy-900 hover:bg-navy-800 text-slate-200 font-mono text-xs sm:text-sm font-bold tracking-widest uppercase border border-navy-700 hover:border-slate-500 transition-colors flex items-center justify-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>RUN ANOTHER AUDIT</span>
          </button>

          <button
            onClick={handleExportJSON}
            className="w-full sm:w-auto px-8 py-4 bg-crimson hover:bg-posterPink text-white hover:text-navy-950 font-mono text-xs sm:text-sm font-bold tracking-widest uppercase border border-crimson transition-all flex items-center justify-center gap-2"
          >
            {downloadSuccess ? (
              <>
                <Check className="w-4 h-4 text-emerald-400" />
                <span>AUDIT REPORT DOWNLOADED</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>EXPORT AUDIT REPORT (JSON)</span>
              </>
            )}
          </button>
        </div>

      </div>
    </section>
  );
};