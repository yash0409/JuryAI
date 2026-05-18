'use client';

import Link from 'next/link';
import { ArrowRight, Scale } from 'lucide-react';

export default function Home() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0a0f1e] via-[#0d1b3e] to-[#060910] animate-gradient-shift" />
      
      {/* Radial glow effect */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent" />
      
      {/* Content container */}
      <div className="relative z-10 flex flex-col items-center justify-center px-6 text-center space-y-10 w-full max-w-4xl mx-auto">
        
        {/* Logo */}
        <div className="flex items-center gap-3">
          <Scale className="w-8 h-8 text-[#3b82f6]" />
          <span className="text-2xl font-bold text-white tracking-wide">VerdictIQ</span>
        </div>

        {/* Headline */}
        <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight" style={{ textShadow: '0 1px 3px rgba(0,0,0,0.5)' }}>
          AI-Powered Legal<br />
          <span className="bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] bg-clip-text text-transparent">
            Document Analysis
          </span>
        </h1>

        {/* Subheadline */}
        <p className="text-[#94a3b8] text-lg md:text-xl font-medium tracking-wide max-w-[600px] leading-relaxed">
          Upload any legal document and get instant AI analysis — summaries, clause extraction, risk detection, and plain-English explanations.
        </p>

        {/* Features row */}
        <div className="flex flex-wrap justify-center gap-4">
          <div className="px-5 py-2.5 rounded-full backdrop-blur-md bg-white/5 border border-white/10 text-[#f1f5f9] text-sm font-medium tracking-wide">
            ⚡ Instant Analysis
          </div>
          <div className="px-5 py-2.5 rounded-full backdrop-blur-md bg-white/5 border border-white/10 text-[#f1f5f9] text-sm font-medium tracking-wide">
            🔍 Clause Extraction
          </div>
          <div className="px-5 py-2.5 rounded-full backdrop-blur-md bg-white/5 border border-white/10 text-[#f1f5f9] text-sm font-medium tracking-wide">
            ⚠️ Risk Detection
          </div>
          <div className="px-5 py-2.5 rounded-full backdrop-blur-md bg-white/5 border border-white/10 text-[#f1f5f9] text-sm font-medium tracking-wide">
            💬 Ask Anything
          </div>
        </div>

        {/* CTA Button */}
        <Link
          href="/upload"
          className="group relative inline-flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-white bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105"
        >
          Start Analyzing
          <ArrowRight className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" />
        </Link>

        {/* Footer text */}
        <p className="text-[#64748b] text-sm font-medium tracking-wide">
          Powered by LLaMA 3.3 · LangGraph · ChromaDB
        </p>
      </div>

      <style jsx>{`
        @keyframes gradient-shift {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
        .animate-gradient-shift {
          background-size: 200% 200%;
          animation: gradient-shift 15s ease infinite;
        }
      `}</style>
    </main>
  );
}