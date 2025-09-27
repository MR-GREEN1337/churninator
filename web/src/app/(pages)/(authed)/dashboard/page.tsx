"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Play,
  Square,
  Loader2,
  BotMessageSquare,
  ArrowRight,
  Search,
  Globe,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

// Mock suggestions, in a real app this would come from user history
const suggestions = [
  "https://vercel.com",
  "https://github.com",
  "https://clerk.com/pricing",
  "https://www.nytimes.com/games/connections",
];

export default function DashboardPage() {
  const [url, setUrl] = useState("");
  const [prompt, setPrompt] = useState(
    "Perform a full analysis of the user onboarding flow.",
  );
  const [agentStatus, setAgentStatus] = useState<
    "idle" | "running" | "finished"
  >("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop =
        logsContainerRef.current.scrollHeight;
    }
  }, [agentLogs]);

  const handleLaunchAgent = () => {
    if (!url || !URL.canParse(url)) {
      alert("Please enter a valid URL.");
      return;
    }
    setAgentStatus("running");
    setAgentLogs([`🚀 Launching agent for ${url}...`]);
    // TODO: Connect to backend and get real jobId
    const newJobId = `simulated_${Date.now()}`;
    setJobId(newJobId);

    // Simulate receiving logs
    const interval = setInterval(() => {
      setAgentLogs((prev) => [
        ...prev,
        `[LOG] Agent is performing an action...`,
      ]);
    }, 2000);
    //
  };

  const handleStopAgent = () => {
    setAgentStatus("idle");
    setJobId(null);
    setAgentLogs([]);
    setUrl(""); // Reset for next run
  };

  return (
    <div className="flex flex-col h-full">
      <AnimatePresence mode="wait">
        {agentStatus === "idle" ? (
          <motion.div
            key="idle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex-1 flex flex-col items-center justify-center p-4"
          >
            <div className="w-full max-w-2xl text-center">
              <BotMessageSquare className="mx-auto h-12 w-12 text-primary mb-4" />
              <h1 className="text-4xl font-bold tracking-tight mb-2">
                Churninator Command Center
              </h1>
              <p className="text-muted-foreground mb-8">
                Enter a target URL and a task to begin your reconnaissance
                mission.
              </p>

              <div className="relative">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://competitor.com/signup"
                  className="pl-10 h-14 text-lg rounded-full shadow-lg"
                />
                <Button
                  type="submit"
                  size="icon"
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full"
                  onClick={handleLaunchAgent}
                  disabled={!url}
                >
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </div>

              <div className="mt-4 flex flex-wrap justify-center gap-2">
                <span className="text-sm text-muted-foreground mr-2">Try:</span>
                {suggestions.map((s) => (
                  <Button
                    key={s}
                    variant="outline"
                    size="sm"
                    className="rounded-full"
                    onClick={() => setUrl(s)}
                  >
                    {s}
                  </Button>
                ))}
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="running"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 h-full p-4 sm:p-6 lg:p-8"
          >
            {/* --- Live Agent View --- */}
            <Card className="lg:col-span-5 h-full flex flex-col">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Live Agent View</CardTitle>
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  <span className="text-sm text-muted-foreground">
                    Status: Running
                  </span>
                </div>
              </CardHeader>
              <CardContent className="flex-1 flex items-center justify-center p-2 bg-black rounded-b-lg">
                {jobId ? (
                  <img
                    src={`http://localhost:8000/api/v1/agent/stream/${jobId}`} // Real URL
                    alt="Live agent view"
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <Loader2 className="h-8 w-8 animate-spin text-white" />
                )}
              </CardContent>
            </Card>

            {/* --- Control & Log Panel --- */}
            <Card className="lg:col-span-2 flex flex-col h-full">
              <CardHeader>
                <CardTitle>Mission Log</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-4 flex-1">
                <div className="text-sm space-y-1">
                  <p>
                    <strong className="font-semibold">Target:</strong>{" "}
                    <span className="font-mono text-muted-foreground">
                      {url}
                    </span>
                  </p>
                  <p>
                    <strong className="font-semibold">Objective:</strong>{" "}
                    <span className="text-muted-foreground">{prompt}</span>
                  </p>
                </div>
                <div
                  ref={logsContainerRef}
                  className="flex-1 bg-muted rounded-md p-4 overflow-y-auto text-sm font-mono whitespace-pre-wrap border"
                >
                  {agentLogs.join("\n")}
                </div>
                <Button
                  onClick={handleStopAgent}
                  variant="destructive"
                  className="w-full"
                >
                  <Square className="mr-2 h-4 w-4" /> Stop Mission
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
