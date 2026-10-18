import React, { useState } from 'react';
import { ShieldCheck, Menu, X, ExternalLink, Terminal } from 'lucide-react';
import { isBackendConfigured } from '../services/api';

export default function Navbar({ onOpenPrivacy, onOpenHowItWorks }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const backendActive = isBackendConfigured();

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            <a href="#" className="flex items-center gap-2 sm:gap-2.5 group min-w-0">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center shadow-lg shadow-teal-500/20 group-hover:scale-105 transition-transform duration-200 shrink-0">
                <ShieldCheck className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <span className="font-extrabold text-base sm:text-xl tracking-tight text-white group-hover:text-teal-300 transition-colors">
                    Sach<span className="text-teal-400">Check</span>
                  </span>
                  <span className="text-[9px] sm:text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-full bg-teal-950/80 border border-teal-500/40 text-teal-300">
                    Hackathon
                  </span>
                </div>
                <p className="text-[10px] sm:text-[11px] text-slate-400 hidden sm:block truncate">Check Before You Share</p>
              </div>
            </a>
          </div>

          {/* Desktop Navigation (lg+ for laptops/desktops) */}
          <nav className="hidden lg:flex items-center gap-4 xl:gap-6 shrink-0">
            <button
              onClick={onOpenHowItWorks}
              className="text-sm text-slate-300 hover:text-teal-300 font-medium transition-colors whitespace-nowrap"
            >
              How It Works
            </button>
            <button
              onClick={onOpenPrivacy}
              className="text-sm text-slate-300 hover:text-teal-300 font-medium transition-colors whitespace-nowrap"
            >
              Privacy & Trust
            </button>

            {/* Mode Indicator */}
            <div
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border whitespace-nowrap ${
                backendActive
                  ? 'bg-emerald-950/70 border-emerald-500/40 text-emerald-300'
                  : 'bg-amber-950/60 border-amber-500/40 text-amber-300'
              }`}
              title={
                backendActive
                  ? 'Connected to live backend API'
                  : 'Running in frontend demo mode. Connect VITE_API_BASE_URL to link your backend.'
              }
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  backendActive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                }`}
              />
              <span>{backendActive ? 'Live API' : 'Demo Mode'}</span>
            </div>
          </nav>

          {/* Tablet & Mobile menu button (under lg) */}
          <div className="flex items-center gap-1.5 sm:gap-2 lg:hidden shrink-0">
            <div
              className={`flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full text-[10px] sm:text-[11px] font-semibold border ${
                backendActive
                  ? 'bg-emerald-950/70 border-emerald-500/40 text-emerald-300'
                  : 'bg-amber-950/60 border-amber-500/40 text-amber-300'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${backendActive ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              <span>{backendActive ? 'Live' : 'Demo'}</span>
            </div>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 sm:p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile & Tablet dropdown */}
        {mobileMenuOpen && (
          <div className="lg:hidden py-4 border-t border-slate-800 space-y-2 animate-fadeIn">
            <button
              onClick={() => {
                onOpenHowItWorks();
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2 text-sm text-slate-200 hover:text-teal-300 hover:bg-slate-900/60 rounded-lg transition-colors flex items-center justify-between"
            >
              <span>How It Works</span>
              <span className="text-xs text-slate-400 font-mono">Guide ➔</span>
            </button>
            <button
              onClick={() => {
                onOpenPrivacy();
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2 text-sm text-slate-200 hover:text-teal-300 hover:bg-slate-900/60 rounded-lg transition-colors flex items-center justify-between"
            >
              <span>Privacy & Trust</span>
              <span className="text-xs text-slate-400 font-mono">Info ➔</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
