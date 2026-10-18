import React, { useState, useEffect } from 'react';
import { fetchStats } from '../services/api';

export default function StatsBar() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const data = await fetchStats();
        if (mounted) setStats(data);
      } catch {
        // Degrade gracefully
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const formatNumber = (num) => {
    if (num === undefined || num === null) return '0';
    return Number(num).toLocaleString();
  };

  const statItems = [
    {
      id: 'stat-total-claims',
      label: 'Verified Claims',
      value: formatNumber(stats?.total_claims ?? 0),
      icon: (
        <svg className="w-3.5 h-3.5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
    {
      id: 'stat-total-fact-checks',
      label: 'Fact Check Records',
      value: formatNumber(stats?.total_fact_checks ?? 0),
      icon: (
        <svg className="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      id: 'stat-search-events',
      label: 'Searches Analyzed',
      value: formatNumber(stats?.total_search_events ?? 0),
      icon: (
        <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
    },
    {
      id: 'stat-active-visitors',
      label: 'Active Visitors (24h)',
      value: formatNumber(stats?.distinct_visitor_ids_24h ?? 0),
      icon: (
        <svg className="w-3.5 h-3.5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
    },
  ];

  return (
    <section className="w-full max-w-5xl mx-auto px-2.5 sm:px-6 pt-2.5 sm:pt-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-1.5 sm:gap-3 w-full">
        {statItems.map((item) => (
          <div
            key={item.id}
            id={item.id}
            className="glass-card rounded-xl p-2 sm:p-3 flex items-center gap-2 border border-slate-800/80 hover:border-slate-700/60 transition-colors w-full min-w-0 overflow-hidden"
          >
            <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg bg-slate-800/80 flex items-center justify-center shrink-0">
              {item.icon}
            </div>
            <div className="min-w-0 flex-1 overflow-hidden">
              {loading ? (
                <div className="h-4 skeleton rounded w-10 sm:w-14 mb-0.5" />
              ) : (
                <p className="text-xs sm:text-base font-bold text-slate-100 font-mono tracking-tight leading-none truncate">
                  {item.value}
                </p>
              )}
              <p className="text-[10px] sm:text-xs text-slate-400 truncate mt-0.5">
                {item.label}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
