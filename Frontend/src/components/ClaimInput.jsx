import React, { useRef } from 'react';

const EXAMPLE_CLAIMS = [
  'The earth is flat',
  'Pakistan won the cricket match',
  'Drinking lemon water cures diabetes completely',
  'NASA confirmed the moon is drifting away from Earth',
];

export default function ClaimInput({ claim, setClaim, onVerify, loading, onClear }) {
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (loading || !claim.trim()) return;
    onVerify(claim);
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  const handleSelectExample = (example) => {
    setClaim(example);
    onVerify(example);
  };

  const remainingChars = 2000 - claim.length;

  return (
    <div className="w-full max-w-full overflow-hidden">
      <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-3 sm:p-5 glow-border-teal shadow-2xl relative w-full overflow-hidden">
        <div className="flex items-center justify-between mb-1.5">
          <label htmlFor="claim-textarea" className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider text-teal-400">
            Enter Claim or Statement to Verify
          </label>
          <span className={`text-[10px] sm:text-[11px] font-mono ${remainingChars < 100 ? 'text-amber-400' : 'text-slate-400'}`}>
            {claim.length}/2000
          </span>
        </div>

        <div className="relative w-full">
          <textarea
            id="claim-textarea"
            ref={textareaRef}
            rows={3}
            maxLength={2000}
            disabled={loading}
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. A viral post claims that eating raw garlic prevents COVID-19..."
            className="w-full bg-slate-900/80 border border-slate-700/80 rounded-xl p-2.5 sm:p-3.5 text-slate-100 placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all resize-none disabled:opacity-50 box-border leading-relaxed"
          />

          {claim && !loading && (
            <button
              type="button"
              onClick={onClear}
              title="Clear input"
              className="absolute top-2 right-2 text-slate-400 hover:text-slate-200 bg-slate-800/80 hover:bg-slate-700 rounded-lg p-1 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        <div className="mt-2.5 sm:mt-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="hidden sm:flex text-[11px] text-slate-400 items-center gap-1.5">
            <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[10px]">
              Ctrl
            </kbd>
            <span>+</span>
            <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[10px]">
              Enter
            </kbd>
            <span>to verify instantly</span>
          </div>

          <button
            type="submit"
            id="btn-verify-claim"
            disabled={loading || !claim.trim()}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs sm:text-sm tracking-wide shadow-lg shadow-teal-500/20 hover:shadow-teal-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shrink-0"
          >
            {loading ? (
              <>
                <svg className="animate-spin w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-950" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Analyzing Evidence...</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Verify Claim</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Quick Example Chips */}
      <div className="mt-2.5 sm:mt-3">
        <div className="flex items-center gap-1.5 mb-1.5">
          <span className="text-[10px] sm:text-xs text-slate-400 font-medium">Quick examples:</span>
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          {EXAMPLE_CLAIMS.map((example, idx) => (
            <button
              key={idx}
              type="button"
              disabled={loading}
              onClick={() => handleSelectExample(example)}
              className="text-[10px] sm:text-xs px-2.5 py-1 rounded-lg bg-slate-900/70 hover:bg-slate-800 text-slate-300 hover:text-teal-300 border border-slate-800 hover:border-teal-500/30 transition-all text-left max-w-full break-words"
            >
              "{example}"
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
