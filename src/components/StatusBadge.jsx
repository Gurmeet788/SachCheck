import React from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, HelpCircle, ShieldAlert, ShieldCheck } from 'lucide-react';

export default function StatusBadge({ status, originalVerdict, verdictType }) {
  if (status === 'fact_check_found') {
    const isFalse = verdictType === 'false' || (originalVerdict && originalVerdict.toLowerCase().includes('false'));
    const isTrue = verdictType === 'true' || (originalVerdict && originalVerdict.toLowerCase().includes('true'));

    return (
      <div className="flex flex-wrap items-center gap-2.5">
        {/* App Status */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-950/80 border border-teal-500/50 text-teal-300 text-xs sm:text-sm font-semibold shadow-sm">
          <ShieldCheck className="w-4 h-4 text-teal-400" />
          <span>App Status: Fact-Check Found</span>
        </div>

        {/* Source's Published Verdict */}
        {originalVerdict && (
          <div
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-bold border ${
              isFalse
                ? 'bg-rose-950/70 border-rose-500/50 text-rose-300'
                : isTrue
                ? 'bg-emerald-950/70 border-emerald-500/50 text-emerald-300'
                : 'bg-amber-950/70 border-amber-500/50 text-amber-300'
            }`}
          >
            {isFalse ? (
              <ShieldAlert className="w-4 h-4 text-rose-400" />
            ) : isTrue ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            )}
            <span>Original Source Rating: {originalVerdict}</span>
          </div>
        )}
      </div>
    );
  }

  if (status === 'unverified') {
    return (
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-amber-950/80 border border-amber-500/50 text-amber-300 text-xs sm:text-sm font-semibold shadow-sm">
        <HelpCircle className="w-4 h-4 text-amber-400 shrink-0" />
        <span>App Status: Unverified (No Matching Fact-Check Found)</span>
      </div>
    );
  }

  // Unable to check
  return (
    <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-rose-950/80 border border-rose-500/50 text-rose-300 text-xs sm:text-sm font-semibold shadow-sm">
      <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0" />
      <span>App Status: Unable to Check (Service Failure)</span>
    </div>
  );
}
