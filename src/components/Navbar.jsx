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
          <div className="flex items-center gap-3">
            <a href="#" className="flex items-center gap-2.5 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center shadow-lg shadow-teal-500/20 group-hover:scale-105 transition-transform duration-200">
                <ShieldCheck className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-xl tracking-tight text-white group-hover:text-teal-300 transition-colors">
                    Sach<span className="text-teal-400">Check</span>
                  </span>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-950/80 border border-teal-500/40 text-teal-300">
                    Hackathon
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 hidden sm:block">Check Before You Share</p>
              </div>
            </a>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <button
              onClick={onOpenHowItWorks}
              className="text-sm text-slate-300 hover:text-teal-300 font-medium transition-colors"
            >
              How It Works
            </button>
            <button
              onClick={onOpenPrivacy}
              className="text-sm text-slate-300 hover:text-teal-300 font-medium transition-colors"
            >
              Privacy & Trust
            </button>

            {/* Mode Indicator */}
            <div
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
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

          {/* Mobile menu button */}
          <div className="flex items-center gap-2 md:hidden">
            <div
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
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
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-800 space-y-2 animate-fadeIn">
            <button
              onClick={() => {
                onOpenHowItWorks();
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-200 hover:bg-slate-800 hover:text-teal-300 font-medium"
            >
              How It Works
            </button>
            <button
              onClick={() => {
                onOpenPrivacy();
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-200 hover:bg-slate-800 hover:text-teal-300 font-medium"
            >
              Privacy & Trust
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
