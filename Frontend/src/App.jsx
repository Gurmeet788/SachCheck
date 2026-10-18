import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import ClaimInput from './components/ClaimInput';
import VerificationResult from './components/VerificationResult';
import TrendingSection from './components/TrendingSection';
import StatsBar from './components/StatsBar';
import HowItWorksModal from './components/HowItWorksModal';
import Footer from './components/Footer';
import { verifyClaim } from './services/api';

export default function App() {
  const [page, setPage] = useState('home'); // 'home' | 'trending'
  const [claim, setClaim] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [howItWorksOpen, setHowItWorksOpen] = useState(false);

  // Scroll to result when it arrives
  useEffect(() => {
    if (result) {
      const el = document.getElementById('result-section');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [result]);

  const handleVerify = async (textToVerify) => {
    const text = (textToVerify || claim).trim();
    if (!text) return;
    setLoading(true);
    setResult(null);
    setError('');
    try {
      const data = await verifyClaim(text);
      setResult(data);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setClaim('');
    setResult(null);
    setError('');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectTrendingClaim = (claimText) => {
    setPage('home');
    setClaim(claimText);
    handleVerify(claimText);
  };

  return (
    <div className="min-h-screen w-full max-w-full overflow-x-hidden bg-[#080d1a] text-slate-100 flex flex-col font-sans">
      {/* Background ambient glow */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden max-w-full">
        <div className="absolute -top-40 -left-40 w-[400px] sm:w-[600px] h-[400px] sm:h-[600px] bg-teal-500/5 rounded-full blur-3xl" />
        <div className="absolute top-1/3 right-0 w-[300px] sm:w-[400px] h-[300px] sm:h-[400px] bg-cyan-500/4 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/3 w-[350px] sm:w-[500px] h-[300px] sm:h-[400px] bg-teal-600/4 rounded-full blur-3xl" />
      </div>

      <Navbar
        page={page}
        setPage={setPage}
        onOpenHowItWorks={() => setHowItWorksOpen(true)}
      />

      <main className="flex-1 relative z-10">
        {page === 'home' && (
          <>
            <StatsBar />
            <Hero />

            <section className="w-full max-w-3xl mx-auto px-3 sm:px-6 mt-2">
              <ClaimInput
                claim={claim}
                setClaim={setClaim}
                onVerify={handleVerify}
                loading={loading}
                onClear={handleReset}
              />
            </section>

            {/* Loading skeleton */}
            {loading && (
              <section className="w-full max-w-3xl mx-auto px-3 sm:px-6 mt-6">
                <div className="glass-panel rounded-2xl p-4 sm:p-8 space-y-4 animate-pulse">
                  <div className="h-5 skeleton rounded-lg w-1/3" />
                  <div className="h-4 skeleton rounded-lg w-full" />
                  <div className="h-4 skeleton rounded-lg w-5/6" />
                  <div className="h-4 skeleton rounded-lg w-4/6" />
                  <div className="mt-4 flex gap-3">
                    <div className="h-20 skeleton rounded-xl flex-1" />
                    <div className="h-20 skeleton rounded-xl flex-1" />
                  </div>
                </div>
              </section>
            )}

            {/* Error state */}
            {error && !loading && (
              <section className="w-full max-w-3xl mx-auto px-3 sm:px-6 mt-6 animate-fadeIn">
                <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-rose-500/30">
                  <div className="flex items-start gap-3">
                    <span className="text-rose-400 text-xl">⚠</span>
                    <div>
                      <p className="text-rose-300 font-semibold text-sm">Verification failed</p>
                      <p className="text-slate-400 text-xs sm:text-sm mt-1">{error}</p>
                      <button
                        onClick={() => handleVerify(claim)}
                        className="mt-3 text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 transition-colors"
                      >
                        Retry
                      </button>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Result */}
            <div id="result-section">
              {result && !loading && (
                <VerificationResult
                  result={result}
                  onCheckAnother={handleReset}
                  onRetry={() => handleVerify(claim)}
                />
              )}
            </div>

            {/* Trending preview on home */}
            {!result && !loading && (
              <section className="w-full max-w-3xl mx-auto px-3 sm:px-6 mt-8 sm:mt-12 mb-8">
                <TrendingSection
                  limit={5}
                  compact
                  onViewAll={() => setPage('trending')}
                  onSelectClaim={handleSelectTrendingClaim}
                />
              </section>
            )}
          </>
        )}

        {page === 'trending' && (
          <section className="w-full max-w-4xl mx-auto px-3 sm:px-6 py-6 sm:py-8">
            <TrendingSection
              limit={20}
              onSelectClaim={handleSelectTrendingClaim}
            />
          </section>
        )}
      </main>

      <HowItWorksModal isOpen={howItWorksOpen} onClose={() => setHowItWorksOpen(false)} />
      <Footer onOpenHowItWorks={() => setHowItWorksOpen(true)} setPage={setPage} />
    </div>
  );
}
