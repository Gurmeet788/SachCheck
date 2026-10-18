import React from 'react';

export default function Hero() {
  return (
    <section className="text-center pt-3 sm:pt-6 pb-2 sm:pb-4 px-2.5 sm:px-6 max-w-4xl mx-auto w-full overflow-hidden">
      {/* Badge */}
      <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 sm:px-3 sm:py-1 rounded-full bg-teal-500/10 border border-teal-500/25 text-teal-300 text-[10px] sm:text-xs font-medium mb-2.5 sm:mb-3 shadow-sm max-w-full">
        <svg className="w-3 h-3 text-teal-400 shrink-0 animate-spin" style={{ animationDuration: '6s' }} viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
        </svg>
        <span className="truncate">AI Vector Discovery • Google Fact Check</span>
      </div>

      {/* Main Headline - Balanced typography */}
      <h1 className="text-xl xs:text-2xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-2 sm:mb-3 leading-snug sm:leading-tight break-words">
        Separate Facts from Fiction in <span className="gradient-text neon-teal">Seconds</span>
      </h1>

      {/* Subtitle - Crisp and concise */}
      <p className="text-[11px] xs:text-xs sm:text-sm text-slate-300 max-w-xl mx-auto leading-relaxed mb-3 sm:mb-4 px-1 break-words">
        Submit any news claim or viral rumor. SachCheck pairs <strong className="text-teal-300 font-medium">pgvector semantic discovery</strong> with Google Fact Check to deliver transparent reports.
      </p>

      {/* Trust pill row */}
      <div className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-4 text-[10px] sm:text-xs text-slate-400 font-mono">
        <span className="flex items-center gap-1 bg-slate-900/50 px-2 py-0.5 rounded-md border border-slate-800">
          <span className="text-emerald-400">✓</span> Real-Time
        </span>
        <span className="flex items-center gap-1 bg-slate-900/50 px-2 py-0.5 rounded-md border border-slate-800">
          <span className="text-cyan-400">✓</span> pgvector 768-d
        </span>
        <span className="flex items-center gap-1 bg-slate-900/50 px-2 py-0.5 rounded-md border border-slate-800">
          <span className="text-teal-400">✓</span> Contradiction Guard
        </span>
      </div>
    </section>
  );
}
