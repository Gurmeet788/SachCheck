import React from 'react';
import { ShieldCheck, Heart, Github, ExternalLink } from 'lucide-react';
import { isBackendConfigured } from '../services/api';

export default function Footer({ onOpenPrivacy, onOpenHowItWorks }) {
  const backendActive = isBackendConfigured();

  return (
    <footer className="mt-20 border-t border-slate-800 bg-slate-950/60 py-10 px-4 sm:px-6 text-slate-400 text-xs sm:text-sm">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Brand & Mission */}
        <div className="flex flex-col items-center md:items-start gap-1.5 text-center md:text-left">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-teal-400" />
            <span className="font-bold text-white tracking-tight text-base">
              Sach<span className="text-teal-400">Check</span>
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-300 font-medium">Check Before You Share</span>
          </div>
          <p className="text-xs text-slate-500 max-w-sm">
            Empowering communities to verify claims and halt the viral spread of misleading information.
          </p>
        </div>

        {/* Links */}
        <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400">
          <button
            onClick={onOpenHowItWorks}
            className="hover:text-teal-300 transition-colors"
          >
            How It Works
          </button>
          <button
            onClick={onOpenPrivacy}
            className="hover:text-teal-300 transition-colors"
          >
            Privacy Notice
          </button>
          <span className="text-slate-700 hidden sm:inline">•</span>
          <span className="text-slate-500">
            Status: <span className={backendActive ? 'text-emerald-400' : 'text-amber-400'}>{backendActive ? 'Backend Linked' : 'Demo Mode'}</span>
          </span>
        </div>

        {/* Hackathon Badge */}
        <div className="text-center md:text-right text-xs text-slate-500">
          <p>Built for the Hackathon</p>
          <p className="mt-0.5 text-[11px] text-slate-600">Frontend: React + Vite + Tailwind</p>
        </div>
      </div>
    </footer>
  );
}
