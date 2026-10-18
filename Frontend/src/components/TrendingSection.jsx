import React, { useState, useEffect } from 'react';
import { fetchTrending, verifyClaim } from '../services/api';
import StatusBadge from './StatusBadge';

export default function TrendingSection({ limit = 10, compact = false, onViewAll, onSelectClaim }) {
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('');

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await fetchTrending(limit);
        if (mounted) setTrending(data || []);
      } catch (err) {
        if (mounted) setError(err.message || 'Failed to load trending claims');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, [limit]);

  const filteredItems = filter
    ? trending.filter((item) => item.claim_text.toLowerCase().includes(filter.toLowerCase()))
    : trending;

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse shrink-0" />
            <h2 className="text-base sm:text-lg font-bold text-slate-100 flex items-center gap-2">
              Trending Claims
              <span className="text-[11px] sm:text-xs font-mono font-normal text-slate-400">
                (Last 24h)
              </span>
            </h2>
          </div>
          <p className="text-[11px] sm:text-xs text-slate-400 mt-0.5">
            Most queried statements ranked by unique visitor lookups.
          </p>
        </div>

        {compact && onViewAll && (
          <button
            onClick={onViewAll}
            className="self-start sm:self-auto text-xs font-semibold text-teal-400 hover:text-teal-300 flex items-center gap-1 transition-colors"
          >
            <span>View All</span>
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>

      {/* Search filter for full page */}
      {!compact && (
        <div className="mb-4">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter trending claims by keyword..."
            className="w-full sm:w-72 bg-slate-900/80 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500"
          />
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="space-y-3">
          {[...Array(compact ? 3 : 6)].map((_, i) => (
            <div key={i} className="glass-card rounded-xl p-3 sm:p-4 flex items-center gap-3 animate-pulse">
              <div className="w-6 h-6 skeleton rounded-full shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="h-4 skeleton rounded w-3/4" />
                <div className="h-3 skeleton rounded w-1/4" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="glass-panel rounded-xl p-4 text-xs text-rose-300 border border-rose-500/30">
          Failed to load trending claims: {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredItems.length === 0 && (
        <div className="glass-panel rounded-xl p-6 sm:p-8 text-center text-slate-400 text-xs sm:text-sm">
          <p className="font-medium text-slate-300">No claims recorded yet in the last 24 hours.</p>
          <p className="text-[11px] sm:text-xs text-slate-400 mt-1">
            Submit a claim in the box above to start tracking real-time verification trends.
          </p>
        </div>
      )}

      {/* Items list */}
      {!loading && !error && filteredItems.length > 0 && (
        <div className="space-y-2 sm:space-y-2.5">
          {filteredItems.map((item, index) => (
            <div
              key={item.claim_id}
              onClick={() => onSelectClaim && onSelectClaim(item.claim_text)}
              className={`glass-card rounded-xl p-3 sm:p-4 flex flex-col xs:flex-row xs:items-center justify-between gap-2.5 sm:gap-3 hover:border-teal-500/40 hover:bg-slate-800/50 transition-all group ${
                onSelectClaim ? 'cursor-pointer' : ''
              }`}
            >
              <div className="flex items-start xs:items-center gap-2.5 sm:gap-3 min-w-0 flex-1">
                <span className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-[11px] sm:text-xs font-mono font-bold text-slate-400 flex items-center justify-center shrink-0 mt-0.5 xs:mt-0">
                  {index + 1}
                </span>

                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-medium text-slate-200 group-hover:text-white transition-colors truncate">
                    {item.claim_text}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] sm:text-[11px] font-mono text-slate-400">
                      ID #{item.claim_id}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-[10px] sm:text-[11px] text-cyan-300/90 font-mono flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      {item.distinct_visitor_count} {item.distinct_visitor_count === 1 ? 'visitor' : 'visitors'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="shrink-0 flex items-center justify-end gap-2 self-end xs:self-center">
                <StatusBadge status={item.status} size="sm" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
