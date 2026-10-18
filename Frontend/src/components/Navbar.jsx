import React, { useState, useEffect } from 'react';
import { checkHealth } from '../services/api';

export default function Navbar({ page, setPage, onOpenHowItWorks }) {
  const [backendOnline, setBackendOnline] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    let mounted = true;
    const probe = async () => {
      try {
        await checkHealth();
        if (mounted) setBackendOnline(true);
      } catch {
        if (mounted) setBackendOnline(false);
      }
    };
    probe();
    const interval = setInterval(probe, 30000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [page]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) setMobileMenuOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full max-w-full glass-panel border-b border-slate-800/80 bg-[#080d1a]/95 backdrop-blur-md overflow-hidden">
      <div className="w-full max-w-6xl mx-auto px-2.5 sm:px-6">
        <div className="h-13 sm:h-16 flex items-center justify-between gap-1.5 sm:gap-4 w-full">
          {/* Brand Logo */}
          <button
            onClick={() => setPage('home')}
            className="flex items-center gap-1.5 sm:gap-2.5 group focus:outline-none shrink-0"
          >
            <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-400 p-[1px] shadow-lg shadow-teal-500/20 group-hover:shadow-teal-500/40 transition-shadow">
              <div className="w-full h-full bg-[#080d1a] rounded-[11px] flex items-center justify-center">
                <svg className="w-4 h-4 sm:w-5 sm:h-5 text-teal-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
            </div>
            <div className="flex flex-col text-left">
              <div className="flex items-center gap-1">
                <span className="text-sm sm:text-lg font-bold tracking-tight text-white leading-none">
                  Sach<span className="text-teal-400">Check</span>
                </span>
                <span className="hidden xs:inline-block text-[9px] uppercase font-bold px-1 py-0.5 rounded bg-teal-500/15 text-teal-300 border border-teal-500/30 leading-none">
                  v2.0
                </span>
              </div>
              <span className="hidden sm:inline text-[9px] text-slate-400 tracking-wider font-mono mt-0.5">
                AI VERIFICATION ENGINE
              </span>
            </div>
          </button>

          {/* Center Tabs: Verify & Trending */}
          <nav className="flex items-center gap-0.5 sm:gap-1 bg-slate-900/80 p-0.5 sm:p-1 rounded-xl border border-slate-800 shrink-0">
            <button
              onClick={() => setPage('home')}
              className={`text-[11px] sm:text-sm font-medium px-2 sm:px-3.5 py-1 sm:py-1.5 rounded-lg transition-all ${
                page === 'home'
                  ? 'bg-teal-500/20 text-teal-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Verify
            </button>
            <button
              onClick={() => setPage('trending')}
              className={`text-[11px] sm:text-sm font-medium px-2 sm:px-3.5 py-1 sm:py-1.5 rounded-lg transition-all flex items-center gap-1 sm:gap-1.5 ${
                page === 'trending'
                  ? 'bg-teal-500/20 text-teal-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>Trending</span>
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse hidden xs:inline-block" />
            </button>
          </nav>

          {/* Right Controls - Desktop (md+) */}
          <div className="hidden md:flex items-center gap-2.5 shrink-0">
            <button
              onClick={onOpenHowItWorks}
              className="inline-flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 transition-colors whitespace-nowrap"
            >
              <svg className="w-3.5 h-3.5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>How it works</span>
            </button>

            <div
              title={backendOnline === true ? 'Backend operational' : backendOnline === false ? 'Backend unreachable' : 'Checking status...'}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-[11px] whitespace-nowrap"
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  backendOnline === true
                    ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]'
                    : backendOnline === false
                    ? 'bg-rose-500'
                    : 'bg-amber-400 animate-ping'
                }`}
              />
              <span className="text-slate-400">
                {backendOnline === true ? 'API Live' : backendOnline === false ? 'API Offline' : 'Connecting'}
              </span>
            </div>
          </div>

          {/* Right Controls - Mobile/Tablet (< md) */}
          <div className="flex items-center gap-1.5 md:hidden shrink-0">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 rounded-lg text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 focus:outline-none flex items-center justify-center"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden py-2.5 border-t border-slate-800/80 space-y-1.5 animate-fadeIn bg-[#080d1a]/95">
            <button
              onClick={() => {
                onOpenHowItWorks();
                setMobileMenuOpen(false);
              }}
              className="w-full flex items-center justify-between p-2 rounded-xl bg-slate-900/60 hover:bg-slate-800 text-slate-200 text-xs font-medium border border-slate-800 transition-colors"
            >
              <span className="flex items-center gap-2">
                <svg className="w-3.5 h-3.5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>How Verification Works</span>
              </span>
              <span className="text-[10px] text-teal-400 font-mono">Guide ➔</span>
            </button>

            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/40 text-xs text-slate-400 border border-slate-800/60">
              <span className="flex items-center gap-1.5">
                <span
                  className={`w-2 h-2 rounded-full ${
                    backendOnline === true ? 'bg-emerald-400' : backendOnline === false ? 'bg-rose-500' : 'bg-amber-400'
                  }`}
                />
                <span>FastAPI Backend</span>
              </span>
              <span className="font-mono text-[10px] text-slate-300">
                {backendOnline === true ? 'Live (:8000)' : backendOnline === false ? 'Offline' : 'Connecting'}
              </span>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
