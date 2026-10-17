import React from 'react';
import { Shield, Sparkles, CheckCircle, Search, AlertOctagon } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative pt-10 pb-8 sm:pt-14 sm:pb-12 text-center">
      {/* Background radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] sm:w-[600px] h-[250px] bg-teal-500/10 blur-[120px] pointer-events-none rounded-full" />

      <div className="relative max-w-3xl mx-auto px-4 sm:px-6">
        {/* Hackathon Pill */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/90 border border-slate-700/80 text-xs font-medium text-slate-300 shadow-sm mb-6">
          <span className="flex h-2 w-2 rounded-full bg-teal-400 animate-ping" />
          <span className="text-teal-300 font-semibold">SachCheck Frontend Prototype</span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-400">Misinformation Verification</span>
        </div>

        {/* Hero Heading */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-tight">
          Check Before You <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 via-teal-300 to-cyan-400">Share.</span>
        </h1>

        {/* Subtext */}
        <p className="mt-4 text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Verify viral forwards, news headlines, and suspicious claims against published fact-checks before forwarding them on messaging apps or social networks.
        </p>

        {/* Core Principles Pills */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-900/60 border border-slate-800">
            <CheckCircle className="w-3.5 h-3.5 text-teal-400" />
            <span>Accredited Fact-Checks</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-900/60 border border-slate-800">
            <Shield className="w-3.5 h-3.5 text-teal-400" />
            <span>Zero Invented Scores</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-900/60 border border-slate-800">
            <AlertOctagon className="w-3.5 h-3.5 text-teal-400" />
            <span>Unverified ≠ False Rule</span>
          </div>
        </div>
      </div>
    </section>
  );
}
