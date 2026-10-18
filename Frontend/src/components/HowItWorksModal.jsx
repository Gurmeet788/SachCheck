import React, { useEffect } from 'react';

const PIPELINE_STEPS = [
  {
    step: '01',
    title: 'Text Normalization & Exact Deduplication',
    badge: 'Sub-millisecond',
    description:
      'Removes trailing punctuation, unifies capitalization, strips harmless leading articles, and matches existing claim records to prevent redundant API queries.',
  },
  {
    step: '02',
    title: 'Semantic Vector Discovery (pgvector)',
    badge: 'Gemini 768-d',
    description:
      'When no exact duplicate exists, Google Gemini generates a 768-dimensional semantic embedding vector. PostgreSQL pgvector searches existing claims using cosine similarity.',
  },
  {
    step: '03',
    title: 'AI Equivalence & Contradiction Guard',
    badge: 'Safety Layer',
    description:
      'Opposing claims (e.g. "team won" vs "team did not win") often share high vector similarity. SachCheck applies strict negation analysis and Gemini equivalence classification to prevent unsafe claim merging.',
  },
  {
    step: '04',
    title: 'Google Fact Check Tools API',
    badge: 'Global Authority',
    description:
      'Authoritative fact-checking organizations (Snopes, Reuters, AFP, PolitiFact, etc.) are queried in real time to retrieve publisher verdicts and primary sources.',
  },
  {
    step: '05',
    title: 'Gemini Synthesis & Reporting',
    badge: 'Transparent Verdict',
    description:
      'Gemini summarizes findings strictly based on verified evidence, exposes limitations or missing context, and provides clear, fact-based corrections.',
  },
];

export default function HowItWorksModal({ isOpen, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto animate-fadeIn">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative glass-panel rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-teal-500/30 p-4 sm:p-8 shadow-2xl z-10">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3.5 sm:pb-4 mb-4 sm:mb-6">
          <div className="flex items-center gap-2 sm:gap-2.5">
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center shrink-0">
              <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-white leading-tight">
                How SachCheck Verifies Claims
              </h2>
              <p className="text-[11px] sm:text-xs text-slate-400">
                End-to-end multi-stage fact verification pipeline
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 sm:p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 transition-colors"
          >
            <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Pipeline steps */}
        <div className="space-y-3 sm:space-y-4">
          {PIPELINE_STEPS.map((stepItem) => (
            <div
              key={stepItem.step}
              className="glass-card rounded-xl p-3 sm:p-4 border border-slate-800 flex gap-3 sm:gap-4 items-start"
            >
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-teal-500/15 border border-teal-500/30 text-teal-300 font-mono font-bold text-[11px] sm:text-xs flex items-center justify-center shrink-0">
                {stepItem.step}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center justify-between gap-1.5 sm:gap-2 mb-1">
                  <h3 className="text-xs sm:text-sm font-semibold text-slate-200">
                    {stepItem.title}
                  </h3>
                  <span className="text-[9px] sm:text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-teal-300 border border-slate-700">
                    {stepItem.badge}
                  </span>
                </div>
                <p className="text-[11px] sm:text-xs text-slate-300 leading-relaxed">
                  {stepItem.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Footer info */}
        <div className="mt-4 sm:mt-6 pt-3.5 sm:pt-4 border-t border-slate-800 flex flex-col xs:flex-row items-center justify-between gap-3">
          <p className="text-[10px] sm:text-[11px] text-slate-400 text-center xs:text-left">
            Built with FastAPI, Supabase pgvector, and Google Gemini.
          </p>
          <button
            onClick={onClose}
            className="w-full xs:w-auto text-xs px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold transition-colors text-center"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
