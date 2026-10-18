import React from 'react';

/**
 * Format ISO datetime string to readable local format
 */
function formatDate(dateStr) {
  if (!dateStr) return null;
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return null;
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return null;
  }
}

/**
 * Determine badge color based on rating keywords
 */
function getRatingStyle(rating) {
  if (!rating) return 'bg-slate-700 text-slate-300 border-slate-600';
  const lower = rating.toLowerCase();
  if (lower.includes('false') || lower.includes('pants on fire') || lower.includes('incorrect') || lower.includes('fake')) {
    return 'bg-rose-500/15 text-rose-300 border-rose-500/30';
  }
  if (lower.includes('true') || lower.includes('correct') || lower.includes('accurate')) {
    return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
  }
  if (lower.includes('misleading') || lower.includes('mostly') || lower.includes('partly') || lower.includes('mixture') || lower.includes('half')) {
    return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
  }
  return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30';
}

export default function EvidenceCard({ factCheck }) {
  if (!factCheck) return null;

  const { publisher, rating, source_url, published_at } = factCheck;
  const formattedDate = formatDate(published_at);
  const ratingStyle = getRatingStyle(rating);

  return (
    <div className="glass-card rounded-xl p-3.5 sm:p-5 flex flex-col justify-between hover:border-slate-500/60 transition-all duration-200 group">
      <div>
        <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-teal-400 shrink-0" />
            <span className="font-semibold text-slate-200 text-xs sm:text-sm">{publisher || 'Fact Checker'}</span>
          </div>
          {rating && (
            <span className={`text-[10px] sm:text-xs px-2 sm:px-2.5 py-0.5 rounded-full border font-medium ${ratingStyle}`}>
              {rating}
            </span>
          )}
        </div>

        {formattedDate && (
          <p className="text-xs text-slate-400 mb-3 flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>Published {formattedDate}</span>
          </p>
        )}
      </div>

      {source_url && (
        <a
          href={source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-xs text-teal-400 hover:text-teal-300 transition-colors font-medium mt-2 pt-2 border-t border-slate-800/80 group-hover:border-slate-700/60"
        >
          <span>View Primary Source</span>
          <svg className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}
    </div>
  );
}
