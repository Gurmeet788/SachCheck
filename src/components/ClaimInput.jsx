import React, { useState } from 'react';
import { Search, RotateCcw, AlertCircle, ArrowRight, Loader2, Sparkles } from 'lucide-react';
import { EXAMPLE_CLAIMS } from '../data/demoData';

const MAX_CHARS = 1000;

export default function ClaimInput({
  claim,
  setClaim,
  onVerify,
  loading,
  onClear,
}) {
  const [validationError, setValidationError] = useState('');

  const charCount = claim.length;
  const isNearLimit = charCount > MAX_CHARS * 0.9;
  const isOverLimit = charCount > MAX_CHARS;

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    setValidationError('');

    const trimmed = claim.trim();
    if (!trimmed) {
      setValidationError('Please enter a claim or news statement to verify.');
      return;
    }

    if (trimmed.length < 10) {
      setValidationError('Claim is too brief. Please enter a full sentence or statement for an accurate check.');
      return;
    }

    if (trimmed.length > MAX_CHARS) {
      setValidationError(`Claim exceeds maximum character length (${MAX_CHARS} characters). Please shorten it.`);
      return;
    }

    onVerify(trimmed);
  };

  const handleSelectExample = (exampleText) => {
    setValidationError('');
    setClaim(exampleText);
    onVerify(exampleText);
  };

  const handleClear = () => {
    setValidationError('');
    onClear();
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 sm:px-6">
      <div className="glass-panel p-5 sm:p-7 rounded-2xl shadow-xl shadow-black/40 border border-slate-700/60 relative">
        <form onSubmit={handleSubmit}>
          {/* Label & Counter */}
          <div className="flex items-center justify-between mb-2">
            <label
              htmlFor="claim-input"
              className="text-sm font-semibold text-slate-200 flex items-center gap-2"
            >
              <span>Enter Claim or News Statement</span>
              <span className="text-xs font-normal text-slate-400 hidden sm:inline">
                (from WhatsApp, social media, or web)
              </span>
            </label>
            <span
              className={`text-xs font-mono font-medium ${
                isOverLimit
                  ? 'text-rose-400 font-bold'
                  : isNearLimit
                  ? 'text-amber-400'
                  : 'text-slate-400'
              }`}
            >
              {charCount} / {MAX_CHARS}
            </span>
          </div>

          {/* Text Area */}
          <div className="relative">
            <textarea
              id="claim-input"
              value={claim}
              onChange={(e) => {
                setClaim(e.target.value);
                if (validationError) setValidationError('');
              }}
              rows={4}
              maxLength={MAX_CHARS}
              placeholder="e.g. 'WHO announced 5G mobile networks transmit the coronavirus disease' or paste a viral forwarded message..."
              disabled={loading}
              className="w-full px-4 py-3 bg-slate-900/90 text-slate-100 placeholder-slate-500 rounded-xl border border-slate-700 focus:border-teal-400 focus:ring-2 focus:ring-teal-400/20 focus:outline-none transition-all resize-y min-h-[110px] text-sm sm:text-base leading-relaxed disabled:opacity-60 disabled:cursor-not-allowed"
            />
          </div>

          {/* Validation Error Message */}
          {validationError && (
            <div className="mt-2.5 flex items-center gap-2 text-rose-400 text-xs sm:text-sm bg-rose-950/40 border border-rose-500/30 p-2.5 rounded-lg animate-shake">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{validationError}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-800/80">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              {claim && (
                <button
                  type="button"
                  onClick={handleClear}
                  disabled={loading}
                  className="w-full sm:w-auto px-3 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 rounded-lg border border-slate-700/60 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-50"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Clear Input</span>
                </button>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || !claim.trim()}
              className="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-400 hover:to-teal-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-teal-500/25 hover:shadow-teal-500/40 focus:ring-2 focus:ring-teal-400/40 focus:outline-none transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Verifying Against Records...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Check This Claim</span>
                  <ArrowRight className="w-4 h-4 ml-0.5 opacity-80" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Quick Example Claim Chips */}
        <div className="mt-6 pt-5 border-t border-slate-800/80">
          <div className="flex items-center gap-1.5 mb-2.5 text-xs font-semibold text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            <span>Try Quick Test Examples:</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {EXAMPLE_CLAIMS.map((ex) => (
              <button
                key={ex.id}
                type="button"
                onClick={() => handleSelectExample(ex.text)}
                disabled={loading}
                className="text-xs px-3 py-1.5 rounded-lg bg-slate-800/70 hover:bg-slate-700/80 text-slate-300 hover:text-teal-300 border border-slate-700/60 hover:border-teal-500/40 transition-all text-left flex items-center gap-1.5 group disabled:opacity-50"
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    ex.type === 'debunked'
                      ? 'bg-rose-400'
                      : ex.type === 'verified_true'
                      ? 'bg-teal-400'
                      : ex.type === 'unverified'
                      ? 'bg-amber-400'
                      : 'bg-slate-400'
                  }`}
                />
                <span className="font-medium group-hover:underline">{ex.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
