import React from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  HelpCircle,
  ExternalLink,
  Info,
  CheckCircle,
  RefreshCw,
  Search,
  BookOpen,
  ArrowRight
} from 'lucide-react';
import StatusBadge from './StatusBadge';
import EvidenceCard from './EvidenceCard';
import CopySummaryButton from './CopySummaryButton';

export default function VerificationResult({ result, onRetry, onCheckAnother }) {
  if (!result) return null;

  const {
    status,
    claimReviewed,
    originalVerdict,
    verdictType,
    analysisSummary,
    evidenceSources = [],
    error,
    isDemo,
    demoNote,
    message,
    guidance,
  } = result;

  return (
    <section className="w-full max-w-3xl mx-auto mt-8 px-4 sm:px-6 animate-fadeIn">
      <div className="glass-panel p-5 sm:p-8 rounded-2xl shadow-2xl border border-slate-700/70 relative overflow-hidden">
        {/* Accent top border glow */}
        <div
          className={`absolute top-0 left-0 right-0 h-1.5 ${
            status === 'fact_check_found'
              ? verdictType === 'true'
                ? 'bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-500'
                : 'bg-gradient-to-r from-rose-500 via-amber-500 to-rose-600'
              : status === 'unverified'
              ? 'bg-gradient-to-r from-amber-400 via-amber-500 to-yellow-600'
              : 'bg-gradient-to-r from-rose-500 via-red-600 to-rose-700'
          }`}
        />

        {/* Demo Mode Badge if result is from mock data */}
        {isDemo && (
          <div className="mb-4 p-3 rounded-xl bg-amber-950/60 border border-amber-500/50 text-amber-200 text-xs sm:text-sm flex items-start gap-2.5 shadow-sm">
            <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold uppercase tracking-wider text-amber-300 mr-1.5">DEMO MODE:</span>
              <span>{demoNote || 'Simulated response from dedicated mock service. This is NOT genuine fact-check verification.'}</span>
            </div>
          </div>
        )}

        {/* Header: Status and Copy Summary */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-slate-800">
          <StatusBadge
            status={status}
            originalVerdict={originalVerdict}
            verdictType={verdictType}
          />
          <CopySummaryButton result={result} />
        </div>

        {/* Claim Reviewed Box */}
        <div className="mt-5 p-3.5 sm:p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <p className="text-xs uppercase tracking-wider font-semibold text-slate-400 mb-1">
            Claim Under Verification:
          </p>
          <p className="text-sm sm:text-base font-medium text-slate-100 italic">
            "{claimReviewed}"
          </p>
        </div>

        {/* CASE 1: FACT-CHECK FOUND */}
        {status === 'fact_check_found' && (
          <div className="mt-6 space-y-6">
            {/* Analysis Summary */}
            {analysisSummary && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Key Verification Finding
                </h3>
                <p className="text-sm sm:text-base text-slate-200 leading-relaxed bg-slate-900/40 p-4 rounded-xl border border-slate-800/80">
                  {analysisSummary}
                </p>
              </div>
            )}

            {/* Evidence & Sources List */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-teal-400" />
                  <span>Accredited Fact-Check Sources ({evidenceSources.length})</span>
                </h3>
                <span className="text-xs text-slate-400">Directly cited reports</span>
              </div>

              <div className="space-y-3">
                {evidenceSources.map((ev, idx) => (
                  <EvidenceCard key={ev.id || idx} evidence={ev} index={idx} />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* CASE 2: UNVERIFIED (CRUCIAL ETHICAL PRINCIPLE) */}
        {status === 'unverified' && (
          <div className="mt-6 space-y-5">
            <div className="p-5 rounded-xl bg-amber-950/30 border border-amber-500/30 space-y-3">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm sm:text-base font-bold text-amber-200">
                    No Matching Fact-Check or Evidence Found
                  </h4>
                  <p className="mt-1 text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {message || 'Our database did not find a formal fact-check from accredited agencies matching this exact claim.'}
                  </p>
                </div>
              </div>

              {/* Crucial Ethical Warning Callout */}
              <div className="mt-3 p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs sm:text-sm text-slate-300">
                <div className="flex items-start gap-2.5">
                  <Info className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
                  <p className="leading-relaxed">
                    <strong className="text-white font-semibold">Important Rule:</strong>{' '}
                    <span className="text-amber-300 font-medium">Missing evidence is NEVER proof that a claim is false</span>. 
                    It simply means independent fact-checkers have not reviewed or published findings on this statement yet.
                  </p>
                </div>
              </div>
            </div>

            {/* Actionable Verification Checklist */}
            <div className="p-4 sm:p-5 rounded-xl bg-slate-900/50 border border-slate-800">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-teal-400" />
                <span>Next Steps Before You Share:</span>
              </h4>
              <ul className="space-y-2 text-xs sm:text-sm text-slate-300">
                <li className="flex items-start gap-2">
                  <span className="text-teal-400 font-bold">•</span>
                  <span><strong>Do not forward immediately:</strong> Pausing before sharing stops viral false news chains.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-teal-400 font-bold">•</span>
                  <span><strong>Inspect the primary source:</strong> Check if an official government or recognized news domain published this announcement.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-teal-400 font-bold">•</span>
                  <span><strong>Reverse image/video search:</strong> If an image was attached, verify if it was recycled from an older event.</span>
                </li>
              </ul>
            </div>
          </div>
        )}

        {/* CASE 3: UNABLE TO CHECK (SERVICE FAILURE / ERROR) */}
        {status === 'unable_to_check' && (
          <div className="mt-6 space-y-4">
            <div className="p-5 rounded-xl bg-rose-950/30 border border-rose-500/30">
              <div className="flex items-start gap-3">
                <AlertOctagon className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm sm:text-base font-bold text-rose-200">
                    Unable to Complete Verification Request
                  </h4>
                  <p className="mt-1 text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {error || 'The verification service failed or could not connect to fact-checking databases.'}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={onRetry}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs sm:text-sm font-semibold border border-slate-700 flex items-center gap-2 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Retry Request</span>
              </button>
            </div>
          </div>
        )}

        {/* Card Footer: Reset / Check Another Claim */}
        <div className="mt-7 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>SachCheck • Misinformation Verification</span>
          <button
            onClick={onCheckAnother}
            className="text-teal-400 hover:text-teal-300 font-medium hover:underline flex items-center gap-1"
          >
            <span>Verify Another Claim</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </section>
  );
}
