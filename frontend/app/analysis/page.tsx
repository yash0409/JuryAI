"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2, User, Bot } from "lucide-react";

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
  if (typeof risks === 'string') return risks;
  if (Array.isArray(risks)) {
    return risks
      .map((risk) => {
        return `**${risk.risk_type || 'Unknown Risk'}**\nSeverity: ${risk.severity || 'N/A'}\n${risk.description || ''}\n${risk.details ? 'Details: ' + risk.details : ''}`;
      })
      .join('\n\n---\n\n');
  }
  return 'No risks identified';
}

function formatClauses(clauses: string | ClauseInfo[]): string {
  if (typeof clauses === 'string') return clauses;
  if (Array.isArray(clauses)) {
    return clauses
      .map((clause) => {
        return `**${clause.clause_number || 'Unknown Clause'}**\n${clause.description || ''}`;
      })
      .join('\n\n---\n\n');
  }
  return 'No clauses found';
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const analyzeDocument = async () => {
      if (!collectionId) return;

      try {
        const response = await fetch("http://localhost:8000/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            collection_id: collectionId,
            query: "analyze this document",
          }),
        });

        if (!response.ok) {
          throw new Error("Analysis failed");
        }

        const data = await response.json();
        setResults({
          summary: data.summary || "No summary available",
          clauses: data.clauses || "No clauses found",
          risks: data.risks || "No risks identified",
          explain: data.explain || "No explanation available",
        });
      } catch (error) {
        console.error("Error analyzing document:", error);
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
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          collection_id: collectionId,
          message: userMessage,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response || "No response received" },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: Failed to get response" },
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-[#0a0f1e] text-[#e2e8f0] flex items-center justify-center px-6 py-8">
        <div className="text-center">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-[#3b82f6] mb-4" />
          <p className="text-lg text-[#94a3b8]">Analyzing document...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#0a0f1e] text-[#e2e8f0]">
      <div className="w-full max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <h1 className="text-3xl font-bold mb-6 text-white">Document Analysis</h1>
            <Tabs defaultValue="summary" className="w-full">
              <TabsList className="grid w-full grid-cols-4 mb-6">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="clauses">Clauses</TabsTrigger>
                <TabsTrigger value="risks">Risks</TabsTrigger>
                <TabsTrigger value="explain">Explain</TabsTrigger>
              </TabsList>

              <TabsContent value="summary">
                <Card>
                  <CardHeader>
                    <CardTitle>Document Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="whitespace-pre-wrap">{results.summary}</p>
                    <SourceTags text={results.summary} />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="clauses">
                <Card>
                  <CardHeader>
                    <CardTitle>Key Clauses</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="whitespace-pre-wrap">{formatClauses(results.clauses)}</p>
                    <SourceTags text={typeof results.clauses === 'string' ? results.clauses : formatClauses(results.clauses)} />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="risks">
                <Card>
                  <CardHeader>
                    <CardTitle>Identified Risks</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="whitespace-pre-wrap">{formatRisks(results.risks)}</p>
                    <SourceTags text={typeof results.risks === 'string' ? results.risks : formatRisks(results.risks)} />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="explain">
                <Card>
                  <CardHeader>
                    <CardTitle>Explanation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="whitespace-pre-wrap">{results.explain}</p>
                    <SourceTags text={results.explain} />
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          <div className="lg:col-span-1">
            <div className="w-full rounded-2xl border-l border-white/10 bg-[rgba(255,255,255,0.02)] flex flex-col">
              <div className="p-4 border-b border-white/10">
                <h2 className="text-lg font-semibold text-white">Chat Assistant</h2>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <p className="text-sm text-[#94a3b8] text-center">
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
                      className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.role === "user" ? "bg-[#3b82f6]" : "bg-[rgba(255,255,255,0.06)]"
                      }`}
                    >
                      {message.role === "user" ? (
                        <User className="w-4 h-4 text-white" />
                      ) : (
                        <Bot className="w-4 h-4 text-[#e2e8f0]" />
                      )}
                    </div>
                    <div
                      className={`max-w-[80%] p-3 rounded-xl text-sm ${
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
                    <div className="w-8 h-8 rounded-full bg-[#3b82f6] flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
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
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question..."
                    disabled={isChatLoading}
                    className="flex-1 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] text-white"
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
