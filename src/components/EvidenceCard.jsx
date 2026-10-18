import React from 'react';
import { ExternalLink, Calendar, Building2, BookmarkCheck, FileText } from 'lucide-react';

export default function EvidenceCard({ evidence, index }) {
  const { title, publisher, publishedDate, url, originalRating, keyFinding } = evidence;

  // Format date if available
  const formattedDate = publishedDate
    ? new Date(publishedDate).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : null;

  return (
    <div className="glass-card p-4 sm:p-5 rounded-xl border border-slate-700/60 hover:border-teal-500/40 transition-all duration-200 shadow-md">
      {/* Publisher and Date Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2 text-xs font-semibold text-teal-300">
          <Building2 className="w-3.5 h-3.5 text-teal-400 shrink-0" />
          <span>{publisher || 'Fact-Checking Source'}</span>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-400">
          {formattedDate && (
            <div className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <span>{formattedDate}</span>
            </div>
          )}

          {originalRating && (
            <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[11px] font-medium text-slate-300 border border-slate-700">
              Rating: <strong className="text-white">{originalRating}</strong>
            </span>
          )}
        </div>
      </div>

      {/* Title */}
      <h4 className="mt-3 text-base sm:text-lg font-bold text-white leading-snug group">
        {title}
      </h4>

      {/* Key Finding / Summary */}
      {keyFinding && (
        <div className="mt-2.5 p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 text-xs sm:text-sm text-slate-300 leading-relaxed">
          <div className="flex items-start gap-2">
            <BookmarkCheck className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-200">Fact-Check Finding: </span>
              <span>{keyFinding}</span>
            </div>
          </div>
        </div>
      )}

      {/* Source Link */}
      <div className="mt-3.5 pt-2 flex items-center justify-end">
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-teal-400 hover:text-teal-300 hover:underline transition-colors px-3 py-1.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60"
        >
          <span>View Original Source Report</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
}
