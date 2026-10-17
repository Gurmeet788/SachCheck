import React from 'react';
import { X, Lock, Shield, EyeOff, Server } from 'lucide-react';

export default function PrivacyNotice({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-xl max-h-[90vh] overflow-y-auto rounded-2xl p-6 sm:p-8 border border-slate-700 shadow-2xl relative text-slate-100">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-teal-400">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white">Privacy & Trust Notice</h2>
            <p className="text-xs sm:text-sm text-slate-400">Your privacy is fundamental to SachCheck</p>
          </div>
        </div>

        <div className="space-y-4 text-xs sm:text-sm text-slate-300 leading-relaxed">
          <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start gap-3">
            <EyeOff className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-white block mb-0.5">No Personal Data Collection</strong>
              SachCheck does not require sign-up, email addresses, phone numbers, or account creation.
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start gap-3">
            <Server className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-white block mb-0.5">Anonymous Query Matching</strong>
              Claims entered are strictly used to cross-reference public fact-checking repositories. We do not correlate queries with your IP address or personal identity.
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start gap-3">
            <Shield className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-white block mb-0.5">No API Key Leakage</strong>
              All client-side code complies with strict frontend security practices. Sensitive API credentials remain securely contained on backend servers.
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-semibold text-xs sm:text-sm transition-colors"
          >
            I Understand
          </button>
        </div>
      </div>
    </div>
  );
}
