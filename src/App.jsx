import React, { useState } from 'react';
import Navbar from './components/Navbar';
import DemoModeBanner from './components/DemoModeBanner';
import Hero from './components/Hero';
import ClaimInput from './components/ClaimInput';
import VerificationResult from './components/VerificationResult';
import HowItWorks from './components/HowItWorks';
import PrivacyNotice from './components/PrivacyNotice';
import Footer from './components/Footer';
import { verifyClaim } from './services/api';

export default function App() {
  const [claim, setClaim] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [howItWorksOpen, setHowItWorksOpen] = useState(false);
  const [privacyOpen, setPrivacyOpen] = useState(false);

  const handleVerify = async (textToVerify) => {
    const text = textToVerify || claim;
    if (!text || !text.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await verifyClaim(text);
      setResult(response);
    } catch (err) {
      setResult({
        status: 'unable_to_check',
        claimReviewed: text,
        error: err.message || 'An unexpected error occurred during verification.',
        isDemo: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setClaim('');
    setResult(null);
  };

  const handleRetry = () => {
    if (claim) {
      handleVerify(claim);
    }
  };

  const handleCheckAnother = () => {
    setClaim('');
    setResult(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#0a0f1d] text-slate-100 flex flex-col font-sans selection:bg-teal-500 selection:text-white relative">
      {/* Top Demo Banner */}
      <DemoModeBanner />

      {/* Main Header / Navbar */}
      <Navbar
        onOpenHowItWorks={() => setHowItWorksOpen(true)}
        onOpenPrivacy={() => setPrivacyOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        <Hero />

        <ClaimInput
          claim={claim}
          setClaim={setClaim}
          onVerify={handleVerify}
          loading={loading}
          onClear={handleClear}
        />

        <VerificationResult
          result={result}
          onRetry={handleRetry}
          onCheckAnother={handleCheckAnother}
        />
      </main>

      {/* How It Works Modal */}
      <HowItWorks
        isOpen={howItWorksOpen}
        onClose={() => setHowItWorksOpen(false)}
      />

      {/* Privacy Notice Modal */}
      <PrivacyNotice
        isOpen={privacyOpen}
        onClose={() => setPrivacyOpen(false)}
      />

      {/* Footer */}
      <Footer
        onOpenHowItWorks={() => setHowItWorksOpen(true)}
        onOpenPrivacy={() => setPrivacyOpen(true)}
      />
    </div>
  );
}
