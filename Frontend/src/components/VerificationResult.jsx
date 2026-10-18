import React, { useState } from 'react';
import StatusBadge from './StatusBadge';
import EvidenceCard from './EvidenceCard';

export default function VerificationResult({ result, onCheckAnother, onRetry }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const { claim_id, claim_text, status, message, fact_checks = [], report } = result;

  const handleCopyReport = () => {
    const textToCopy = `[SachCheck Fact-Check Report]
Claim: "${claim_text}"
Status: ${status}
Summary: ${report?.summary || message || 'No summary available'}
Suggested Correction: ${report?.suggested_correction || 'N/A'}
Verified by SachCheck (ID: ${claim_id})`;

    navigator.clipboard?.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <section className="w-full max-w-3xl mx-auto px-3 sm:px-6 mt-6 sm:mt-8 space-y-4 sm:space-y-6 animate-fadeIn">
      {/* Main Claim Header Card */}
      <div className="glass-panel rounded-2xl p-3.5 sm:p-6 glow-border-teal">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
            <StatusBadge status={status} size="md" />
            <span className="text-[11px] sm:text-xs font-mono text-slate-400">
              Claim ID: #{claim_id}
            </span>
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={handleCopyReport}
              className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-2 sm:py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 transition-colors whitespace-nowrap min-w-0"
            >
              {copied ? (
                <>
                  <svg className="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-emerald-300 font-medium">Copied!</span>
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                  </svg>
                  <span>Share Report</span>
                </>
              )}
            </button>
            <button
              onClick={onCheckAnother}
              className="flex-1 sm:flex-initial inline-flex items-center justify-center text-xs text-teal-400 hover:text-teal-300 px-3 py-2 sm:py-1.5 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 transition-colors font-medium whitespace-nowrap min-w-0"
            >
              Check Another
            </button>
          </div>
        </div>

        {/* Claim text */}
        <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800">
          <p className="text-xs uppercase font-mono tracking-wider text-slate-400 mb-1">
            Submitted Claim Statement
          </p>
          <p className="text-base sm:text-lg font-medium text-slate-100 italic">
            "{claim_text}"
          </p>
        </div>

        {message && (
          <p className="mt-3 text-xs text-slate-400 flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 text-teal-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{message}</span>
          </p>
        )}
      </div>

      {/* Gemini AI Synthesis Report */}
      {report && (
        <div className="glass-panel rounded-2xl p-4 sm:p-6 border border-teal-500/20 space-y-4 sm:space-y-5">
          <div className="flex flex-col xs:flex-row xs:items-center items-start justify-between gap-2 border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-teal-400 animate-pulse shrink-0" />
              <h2 className="text-sm sm:text-base font-bold text-slate-100 uppercase tracking-wide">
                Gemini Intelligence Analysis
              </h2>
            </div>
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full border font-medium ${
                report.evidence_sufficient
                  ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                  : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
              }`}
            >
              {report.evidence_sufficient ? 'Evidence Sufficient' : 'Evidence Incomplete'}
            </span>
          </div>

          {/* Executive Summary */}
          {report.summary && (
            <div>
              <h3 className="text-xs uppercase font-bold text-teal-300 tracking-wider mb-1.5">
                Executive Summary
              </h3>
              <p className="text-xs sm:text-sm text-slate-200 leading-relaxed bg-slate-900/40 p-3 sm:p-3.5 rounded-xl border border-slate-800/80 break-words">
                {report.summary}
              </p>
            </div>
          )}

          {/* Suggested Correction Callout */}
          {report.suggested_correction && (
            <div className="rounded-xl p-4 bg-teal-950/30 border border-teal-500/30">
              <div className="flex items-center gap-2 mb-1.5">
                <svg className="w-4 h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-xs uppercase font-bold text-teal-300 tracking-wider">
                  Fact-Based Correction & Clarification
                </h3>
              </div>
              <p className="text-sm text-teal-100 font-medium leading-relaxed">
                {report.suggested_correction}
              </p>
            </div>
          )}

          {/* Evidence Analysis */}
          {report.evidence_analysis && (
            <div>
              <h3 className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-1.5">
                Detailed Evidence Breakdown
              </h3>
              <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/40 p-3.5 rounded-xl border border-slate-800/80 whitespace-pre-line">
                {report.evidence_analysis}
              </p>
            </div>
          )}

          {/* Known Limitations / Missing Scope */}
          {report.limitations && (
            <div className="text-xs text-slate-400 bg-slate-900/40 p-3 rounded-xl border border-slate-800/60">
              <p className="font-semibold text-slate-300 mb-1">Scope & Limitations:</p>
              <p>{report.limitations}</p>
            </div>
          )}
        </div>
      )}

      {/* External Fact Check Articles / Sources */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <span>Authoritative Sources & Fact Checks</span>
            <span className="text-xs font-mono font-normal text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded-full border border-teal-500/20">
              {fact_checks.length} {fact_checks.length === 1 ? 'source' : 'sources'}
            </span>
          </h2>
        </div>

        {fact_checks.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            {fact_checks.map((fc) => (
              <EvidenceCard key={fc.id || fc.source_url} factCheck={fc} />
            ))}
          </div>
        ) : (
          <div className="glass-panel rounded-xl p-5 text-center text-slate-400 text-sm">
            <p>No external fact-check database entries were found for this specific claim.</p>
            <p className="text-xs text-slate-400 mt-1">
              The statement has been registered in the database for tracking and future matching.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
