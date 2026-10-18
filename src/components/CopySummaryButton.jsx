import React, { useState } from 'react';
import { Copy, Check, Share2 } from 'lucide-react';

export default function CopySummaryButton({ result }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const generateSummaryText = () => {
    const { status, claimReviewed, originalVerdict, analysisSummary, evidenceSources, isDemo } = result;

    let text = `🔍 SachCheck Verification Summary\n`;
    text += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    text += `Claim Checked: "${claimReviewed}"\n\n`;

    if (status === 'fact_check_found') {
      text += `Status: Fact-Check Found\n`;
      if (originalVerdict) {
        text += `Original Source Verdict: ${originalVerdict}\n`;
      }
      if (analysisSummary) {
        text += `Finding: ${analysisSummary}\n\n`;
      }
      if (evidenceSources && evidenceSources.length > 0) {
        text += `Sources:\n`;
        evidenceSources.forEach((ev, i) => {
          text += `  • ${ev.publisher}: ${ev.title}\n    Link: ${ev.url}\n`;
        });
      }
    } else if (status === 'unverified') {
      text += `Status: Unverified\n`;
      text += `Note: No matching fact-check found in public databases.\n`;
      text += `Crucial Rule: Unverified does NOT mean false. Avoid forwarding until confirmed with primary sources.\n`;
    } else {
      text += `Status: Unable to Check (Service Error)\n`;
      text += `Note: Verification service was temporarily unreachable.\n`;
    }

    if (isDemo) {
      text += `\n[DEMO MODE: Generated for UI testing - Not live verification]\n`;
    }

    text += `\n🛡️ "Check Before You Share" — SachCheck`;
    return text;
  };

  const handleCopy = async () => {
    try {
      const summary = generateSummaryText();
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error('Failed to copy summary to clipboard', err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-3.5 py-2 sm:py-1.5 rounded-lg bg-teal-950/80 hover:bg-teal-900 border border-teal-500/50 hover:border-teal-400 text-teal-300 hover:text-white text-xs font-semibold shadow-sm transition-all duration-150 active:scale-95"
      title="Copy verification summary to clipboard for sharing on WhatsApp or Twitter"
    >
      {copied ? (
        <>
          <Check className="w-3.5 h-3.5 text-teal-300" />
          <span className="text-teal-200">Summary Copied!</span>
        </>
      ) : (
        <>
          <Copy className="w-3.5 h-3.5" />
          <span>Copy Shareable Summary</span>
        </>
      )}
    </button>
  );
}
