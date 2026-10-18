import React, { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { isDemoMode } from '../services/api';

export default function DemoModeBanner() {
  const [dismissed, setDismissed] = useState(false);
  const demoActive = isDemoMode();

  if (!demoActive || dismissed) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-amber-950/70 via-slate-900 to-amber-950/70 border-b border-amber-500/30 text-amber-200 text-xs sm:text-sm py-2.5 px-4">
      <div className="max-w-6xl mx-auto flex items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5 sm:mt-0" />
          <p className="leading-tight">
            <strong className="font-bold uppercase tracking-wider text-amber-300">DEMO MODE ACTIVE:</strong>{' '}
            Using dedicated mock service. Showing pre-configured hackathon test scenarios. <span className="underline decoration-amber-400 font-semibold">Not live verification</span>. 
            To connect FastAPI: set <code className="bg-slate-800 px-1 py-0.5 rounded text-amber-100 font-mono text-[11px]">VITE_USE_DEMO=false</code> and <code className="bg-slate-800 px-1 py-0.5 rounded text-amber-100 font-mono text-[11px]">VITE_API_BASE_URL</code> in <code className="bg-slate-800 px-1 py-0.5 rounded text-amber-100 font-mono text-[11px]">.env</code>.
          </p>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="text-amber-400 hover:text-white p-1 rounded-md hover:bg-amber-900/40 transition-colors shrink-0"
          aria-label="Dismiss banner"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
