import React from 'react';
import { X, Search, ShieldCheck, Scale, AlertTriangle, ExternalLink } from 'lucide-react';

export default function HowItWorks({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl p-6 sm:p-8 border border-slate-700 shadow-2xl relative text-slate-100">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-teal-400">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white">How SachCheck Works</h2>
            <p className="text-xs sm:text-sm text-slate-400">Our Fact-Checking & Ethical Verification Architecture</p>
          </div>
        </div>

        {/* 3 Step Flow */}
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start gap-3.5">
            <div className="w-7 h-7 rounded-lg bg-teal-500/20 text-teal-400 font-bold flex items-center justify-center text-sm shrink-0">
              1
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Enter Viral Claim</h3>
              <p className="mt-1 text-xs text-slate-300 leading-relaxed">
                Paste any questionable message, viral forward from WhatsApp, or social media headline into SachCheck.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start gap-3.5">
            <div className="w-7 h-7 rounded-lg bg-teal-500/20 text-teal-400 font-bold flex items-center justify-center text-sm shrink-0">
              2
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Cross-Reference Accredited Registries</h3>
              <p className="mt-1 text-xs text-slate-300 leading-relaxed">
                The claim is matched against peer-reviewed databases and accredited fact-checking bodies (e.g. WHO, Reuters, PIB, Snopes, FactCheck.org).
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start gap-3.5">
            <div className="w-7 h-7 rounded-lg bg-teal-500/20 text-teal-400 font-bold flex items-center justify-center text-sm shrink-0">
              3
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Check Before You Share</h3>
              <p className="mt-1 text-xs text-slate-300 leading-relaxed">
                Review the publisher's verified citations and copy a one-click summary to inform groups before harmful disinformation spreads.
              </p>
            </div>
          </div>
        </div>

        {/* Strict Ethical Guardrails */}
        <div className="mt-6 p-4 rounded-xl bg-teal-950/30 border border-teal-500/30 space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-teal-300 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-teal-400" />
            <span>Our 3 Core Ethical Commitments</span>
          </h4>
          <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
            <li><strong className="text-white">Unverified is NOT False:</strong> Lack of published evidence is never treated as a debunking verdict.</li>
            <li><strong className="text-white">Zero Fabricated Confidence:</strong> We never generate arbitrary AI percentages (e.g., "87% True").</li>
            <li><strong className="text-white">Publisher Attribution:</strong> We show the original publisher's exact rating and link directly to their source.</li>
          </ul>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-semibold text-xs sm:text-sm transition-colors"
          >
            Got it, thanks
          </button>
        </div>
      </div>
    </div>
  );
}
