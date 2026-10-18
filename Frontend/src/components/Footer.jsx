import React from 'react';

export default function Footer({ onOpenHowItWorks, setPage }) {
  return (
    <footer className="w-full border-t border-slate-800/80 bg-[#060a14] mt-12 sm:mt-16 text-slate-400">
      <div className="max-w-6xl mx-auto px-3 sm:px-6 py-8 sm:py-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8 mb-8">
          {/* Brand Column */}
          <div className="space-y-3 sm:col-span-2 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-teal-500/20 border border-teal-500/40 flex items-center justify-center">
                <svg className="w-3.5 h-3.5 text-teal-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span className="text-base font-bold text-white tracking-tight">
                Sach<span className="text-teal-400">Check</span>
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
              Empowering internet users with verified information through semantic vector retrieval, Google Fact Check Tools API, and Google Gemini AI.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
              Navigation
            </h4>
            <ul className="space-y-1.5 text-xs">
              <li>
                <button
                  onClick={() => setPage('home')}
                  className="hover:text-teal-400 transition-colors"
                >
                  Verify Claims
                </button>
              </li>
              <li>
                <button
                  onClick={() => setPage('trending')}
                  className="hover:text-teal-400 transition-colors"
                >
                  Trending Claims (24h)
                </button>
              </li>
              <li>
                <button
                  onClick={onOpenHowItWorks}
                  className="hover:text-teal-400 transition-colors"
                >
                  Pipeline Architecture
                </button>
              </li>
            </ul>
          </div>

          {/* Transparency & AI Ethics Notice */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
              Transparency & Ethics
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              SachCheck synthesizes findings strictly based on verified evidence from accredited fact-checkers. All synthesis includes full source attribution.
            </p>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <p>© {new Date().getFullYear()} SachCheck. All rights reserved.</p>
          <p className="font-mono text-[11px] text-slate-400">
            Powered by FastAPI • Supabase pgvector • Google Gemini
          </p>
        </div>
      </div>
    </footer>
  );
}
