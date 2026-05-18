"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Send,
  Loader2,
  User,
  Bot,
  FileText,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

function extractClauseReferences(text: string): string[] {
  if (!text) return [];
  const regex = /(?:Clause\s+(\d+(?:\.\d+)*))|(?:§\s*(\d+(?:\.\d+)*))/gi;
  const references: string[] = [];
  let match;
  while ((match = regex.exec(text)) !== null) {
    const clauseNum = match[1] || match[2];
    if (clauseNum) {
      const formattedRef = `Clause ${clauseNum}`;
      if (!references.includes(formattedRef)) {
        references.push(formattedRef);
      }
    }
  }
  return references;
}

function SourceTags({ text }: { text: string }) {
  const references = extractClauseReferences(text);
  if (references.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-white/10">
      {references.map((ref, index) => (
        <span
          key={index}
          className="inline-flex items-center rounded-full bg-[rgba(99,102,241,0.15)] px-3 py-1 text-xs font-medium text-[#818cf8] border border-[rgba(99,102,241,0.3)]"
        >
          Source: {ref}
        </span>
      ))}
    </div>
  );
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface RiskInfo {
  risk_type: string;
  description: string;
  severity: string;
  details: string;
}

interface ClauseInfo {
  clause_number: string;
  description: string;
}

interface AnalysisResults {
  summary: string;
  clauses: string | ClauseInfo[];
  risks: string | RiskInfo[];
  explain: string;
}

function formatRisks(risks: string | RiskInfo[]): string {
  if (typeof risks === "string") return risks;
  if (Array.isArray(risks)) {
    return risks
      .map((risk) => {
        return `${risk.risk_type || "Unknown Risk"} — Severity: ${risk.severity || "N/A"}\n${risk.description || ""}${risk.details ? "\nDetails: " + risk.details : ""}`;
      })
      .join("\n\n");
  }
  return "No risks identified";
}

function formatClauses(clauses: string | ClauseInfo[]): string {
  if (typeof clauses === "string") return clauses;
  if (Array.isArray(clauses)) {
    return clauses
      .map((clause) => {
        return `${clause.clause_number || "Unknown Clause"}\n${clause.description || ""}`;
      })
      .join("\n\n");
  }
  return "No clauses found";
}

function getSeverityColor(text: string): string {
  const lower = text.toLowerCase();
  if (lower.includes("high") || lower.includes("critical"))
    return "text-red-400";
  if (lower.includes("medium") || lower.includes("moderate"))
    return "text-yellow-400";
  return "text-green-400";
}

function RiskCard({ risk }: { risk: RiskInfo }) {
  return (
    <div className="p-3 rounded-lg bg-white/5 border border-white/10 space-y-1">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-white text-sm">
          {risk.risk_type || "Unknown Risk"}
        </span>
        <span
          className={`text-xs font-medium px-2 py-0.5 rounded-full border ${getSeverityColor(risk.severity || "")} border-current bg-current/10`}
        >
          {risk.severity || "N/A"}
        </span>
      </div>
      {risk.description && (
        <p className="text-xs text-[#94a3b8] leading-relaxed">
          {risk.description}
        </p>
      )}
      {risk.details && (
        <p className="text-xs text-[#64748b] leading-relaxed">{risk.details}</p>
      )}
    </div>
  );
}

function CollapsibleCard({
  title,
  children,
  defaultOpen = true,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-xl border border-white/10 bg-[rgba(255,255,255,0.03)] overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-white/5 transition-colors"
      >
        <span className="font-semibold text-white text-base">{title}</span>
        {open ? (
          <ChevronUp className="w-4 h-4 text-[#94a3b8]" />
        ) : (
          <ChevronDown className="w-4 h-4 text-[#94a3b8]" />
        )}
      </button>
      {open && (
        <div className="px-5 pb-5 border-t border-white/10">{children}</div>
      )}
    </div>
  );
}

export default function AnalysisPage() {
  const searchParams = useSearchParams();
  const collectionId = searchParams.get("id");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [results, setResults] = useState<AnalysisResults>({
    summary: "",
    clauses: "",
    risks: "",
    explain: "",
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const analyzeDocument = async () => {
      if (!collectionId) return;
      try {
        const response = await fetch("http://localhost:8000/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            collection_id: collectionId,
            query: "analyze this document",
          }),
        });
        if (!response.ok) throw new Error("Analysis failed");
        const data = await response.json();
        setResults({
          summary: data.summary || "No summary available",
          clauses: data.clauses || "No clauses found",
          risks: data.risks || "No risks identified",
          explain: data.explain || "No explanation available",
        });
      } catch {
        setResults({
          summary: "Error loading summary",
          clauses: "Error loading clauses",
          risks: "Error loading risks",
          explain: "Error loading explanation",
        });
      } finally {
        setIsLoading(false);
      }
    };
    analyzeDocument();
  }, [collectionId]);

  const handleSendMessage = async () => {
    if (!chatInput.trim() || !collectionId) return;
    const userMessage = chatInput.trim();
    setChatInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsChatLoading(true);
    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ collection_id: collectionId, message: userMessage }),
      });
      if (!response.ok) throw new Error("Chat request failed");
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response || "No response received" },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: Failed to get response" },
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-[#0a0f1e] text-[#e2e8f0] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-[#3b82f6] mb-4" />
          <p className="text-lg text-[#94a3b8]">Analyzing document...</p>
        </div>
      </main>
    );
  }

  const risksArray = Array.isArray(results.risks) ? results.risks : null;
  const clausesText =
    typeof results.clauses === "string"
      ? results.clauses
      : formatClauses(results.clauses);

  return (
    <main className="min-h-screen bg-[#0a0f1e] text-[#e2e8f0]">
      <div className="w-full max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <FileText className="w-6 h-6 text-[#3b82f6]" />
          <h1 className="text-2xl font-bold text-white">Document Analysis</h1>
        </div>

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* LEFT COLUMN — stacked analysis cards */}
          <div className="flex flex-col gap-4">
            {/* Analysis card (Summary + Clauses) */}
            <CollapsibleCard title="Analysis">
              <div className="pt-4 space-y-4">
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-[#64748b] mb-2">
                    Summary
                  </h3>
                  <p className="text-sm text-[#cbd5e1] leading-relaxed whitespace-pre-wrap">
                    {results.summary}
                  </p>
                  <SourceTags text={results.summary} />
                </div>
                <div className="border-t border-white/10 pt-4">
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-[#64748b] mb-2">
                    Key Clauses
                  </h3>
                  <p className="text-sm text-[#cbd5e1] leading-relaxed whitespace-pre-wrap">
                    {clausesText}
                  </p>
                  <SourceTags text={clausesText} />
                </div>
              </div>
            </CollapsibleCard>

            {/* Risks card */}
            <CollapsibleCard title="Risks" defaultOpen={true}>
              <div className="pt-4">
                {risksArray ? (
                  <div className="space-y-3">
                    {risksArray.map((risk, i) => (
                      <RiskCard key={i} risk={risk} />
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-[#cbd5e1] leading-relaxed whitespace-pre-wrap">
                    {typeof results.risks === "string"
                      ? results.risks
                      : formatRisks(results.risks)}
                  </p>
                )}
              </div>
            </CollapsibleCard>

            {/* Explanation card */}
            <CollapsibleCard title="Plain-English Explanation" defaultOpen={false}>
              <div className="pt-4">
                <p className="text-sm text-[#cbd5e1] leading-relaxed whitespace-pre-wrap">
                  {results.explain}
                </p>
                <SourceTags text={results.explain} />
              </div>
            </CollapsibleCard>
          </div>

          {/* RIGHT COLUMN — document preview + chat */}
          <div className="flex flex-col gap-4">
            {/* Document preview panel */}
            <div className="rounded-xl border border-white/10 bg-[rgba(255,255,255,0.03)] overflow-hidden">
              <div className="px-5 py-4 border-b border-white/10 flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#3b82f6]" />
                <span className="font-semibold text-white text-base">
                  Document Preview
                </span>
              </div>
              <div className="p-5 min-h-[320px] flex flex-col items-center justify-center">
                {/* Simulated document paper */}
                <div className="w-full max-w-xs bg-white rounded-md shadow-2xl shadow-black/50 p-6 space-y-2">
                  {Array.from({ length: 12 }).map((_, i) => (
                    <div
                      key={i}
                      className={`h-2 rounded-full bg-gray-200 ${
                        i === 0
                          ? "w-3/4"
                          : i % 5 === 0
                            ? "w-1/2"
                            : i % 3 === 0
                              ? "w-5/6"
                              : "w-full"
                      }`}
                    />
                  ))}
                  <div className="pt-2 space-y-2">
                    {Array.from({ length: 8 }).map((_, i) => (
                      <div
                        key={i}
                        className={`h-2 rounded-full bg-gray-100 ${
                          i % 4 === 0 ? "w-2/3" : "w-full"
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <p className="mt-4 text-xs text-[#64748b]">
                  Document ID: {collectionId ?? "—"}
                </p>
              </div>
            </div>

            {/* Chat assistant */}
            <div className="rounded-xl border border-white/10 bg-[rgba(255,255,255,0.03)] flex flex-col">
              <div className="px-5 py-4 border-b border-white/10">
                <h2 className="font-semibold text-white text-base">
                  Chat Assistant
                </h2>
                <p className="text-xs text-[#64748b] mt-0.5">
                  Ask anything about this document
                </p>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-72">
                {messages.length === 0 && (
                  <p className="text-sm text-[#94a3b8] text-center py-6">
                    Ask questions about your document...
                  </p>
                )}
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex items-start gap-3 ${
                      message.role === "user" ? "flex-row-reverse" : ""
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.role === "user"
                          ? "bg-[#3b82f6]"
                          : "bg-[rgba(255,255,255,0.06)]"
                      }`}
                    >
                      {message.role === "user" ? (
                        <User className="w-3.5 h-3.5 text-white" />
                      ) : (
                        <Bot className="w-3.5 h-3.5 text-[#e2e8f0]" />
                      )}
                    </div>
                    <div
                      className={`max-w-[80%] p-3 rounded-xl text-sm leading-relaxed ${
                        message.role === "user"
                          ? "bg-[#3b82f6] text-white"
                          : "bg-[rgba(255,255,255,0.06)] text-[#e2e8f0]"
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}
                {isChatLoading && (
                  <div className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-[rgba(255,255,255,0.06)] flex items-center justify-center">
                      <Bot className="w-3.5 h-3.5 text-[#e2e8f0]" />
                    </div>
                    <div className="bg-[rgba(255,255,255,0.06)] p-3 rounded-xl flex gap-1 items-center">
                      <span className="w-2 h-2 bg-[#94a3b8] rounded-full animate-bounce" />
                      <span className="w-2 h-2 bg-[#94a3b8] rounded-full animate-bounce [animation-delay:0.2s]" />
                      <span className="w-2 h-2 bg-[#94a3b8] rounded-full animate-bounce [animation-delay:0.4s]" />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="p-4 border-t border-white/10">
                <div className="flex gap-2">
                  <Input
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a question..."
                    disabled={isChatLoading}
                    className="flex-1 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] text-white placeholder:text-[#64748b]"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={isChatLoading || !chatInput.trim()}
                    size="icon"
                    className="bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
