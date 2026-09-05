import { useState } from 'react';
import type {
  ProductData,
  AnalysisStage,
  AuditResponse,
  ScoreResponse,
} from './types';
import {
  generatePrompts,
  getAudit,
  getScore,
  ingestProduct,
  runSimulation,
} from './api';
import { Hero } from './components/Hero';
import { ProductInput } from './components/ProductInput';
import { AnalysisLoader } from './components/AnalysisLoader';
import { Pipeline } from './components/Pipeline';
import { ResultAudit } from './components/ResultAudit';

export function App() {
  const [stage, setStage] = useState<AnalysisStage>('idle');
  const [currentProduct, setCurrentProduct] = useState<ProductData | null>(null);
  const [merchantId, setMerchantId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prompts, setPrompts] = useState<unknown[]>([]);
  const [simulation, setSimulation] = useState<unknown | null>(null);
  const [audit, setAudit] = useState<AuditResponse | null>(null);
  const [score, setScore] = useState<ScoreResponse | null>(null);

  const handleStartAnalysis = async (product: ProductData) => {
    setCurrentProduct(product);
    setStage('analyzing');
    setLoading(true);
    setError(null);

    try {
      if (!product.url || !product.imageFile) {
        throw new Error('A product URL and image are required.');
      }

      const ingestion = await ingestProduct(
        product.url,
        product.imageFile,
      );

      setMerchantId(ingestion.id);

      const promptResult = await generatePrompts(
        ingestion.id,
      );

      setPrompts(promptResult.prompts);

      const simulationResult = await runSimulation(
        ingestion.id,
      );

      setSimulation(simulationResult);

      const auditResult = await getAudit(
        ingestion.id,
      );

      setAudit(auditResult);

      const scoreResult = await getScore(
        ingestion.id,
      );

      setScore(scoreResult);
      setStage('pipeline');
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Something went wrong',
      );
      setStage('idle');
    } finally {
      setLoading(false);
    }

    setTimeout(() => {
      window.scrollTo({ top: 150, behavior: 'smooth' });
    }, 100);
  };

  const handleAnalysisLoaderComplete = () => {
    if (!loading) {
      setStage('pipeline');
    }
  };

  const handlePipelineComplete = () => {
    setStage('result');
    setTimeout(() => {
      const resultEl = document.getElementById('audit-result-section');
      resultEl?.scrollIntoView({ behavior: 'smooth' });
    }, 150);
  };

  const handleReset = () => {
    setStage('idle');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const scrollToInput = () => {
    const el = document.getElementById('product-input-section');
    el?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#0D1038] text-slate-100 flex flex-col font-sans selection:bg-crimson selection:text-white">
      
      {/* Hero Section: Editorial Poster Typography */}
      <Hero onScrollToInput={scrollToInput} />

      {/* Main Simulation Stages Flow */}
      <main className="flex-1">
        {error && (
          <div className="bg-crimson px-4 py-3 text-center text-sm font-mono text-white">
            {error}
          </div>
        )}
        
        {stage === 'idle' && (
          <ProductInput 
            onAnalyze={handleStartAnalysis} 
            disabled={false}
          />
        )}

        {stage === 'analyzing' && currentProduct && (
          <AnalysisLoader 
            productTitle={currentProduct.title} 
            onComplete={handleAnalysisLoaderComplete}
          />
        )}

        {stage === 'pipeline' && (
          <Pipeline onAllCompleted={handlePipelineComplete} />
        )}

        {stage === 'result' && currentProduct && (
          <ResultAudit 
            product={currentProduct} 
            onReset={handleReset}
            audit={audit}
            score={score}
            merchantId={merchantId}
            promptCount={prompts.length}
            simulation={simulation}
          />
        )}

      </main>

    </div>
  );
}

export default App;