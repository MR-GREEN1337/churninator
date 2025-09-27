"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, BotMessageSquare, AlertTriangle } from "lucide-react";
import { useParams } from "next/navigation"; // Hook to get URL params

// --- TYPE DEFINITIONS & MOCK DATA ---
// In a real app, these would come from your API client
type AgentRun = {
  id: string;
  name: string;
  status: "RUNNING" | "COMPLETED" | "FAILED";
  targetUrl: string;
  taskPrompt: string;
  createdAt: string; // ISO string
};

const mockAgentRuns: AgentRun[] = [
  {
    id: "run-1",
    name: "Onboard Vercel",
    status: "RUNNING",
    targetUrl: "https://vercel.com",
    createdAt: new Date().toISOString(),
    taskPrompt: "Sign up for a new hobby account.",
  },
  {
    id: "run-2",
    name: "Test Clerk Signup",
    status: "RUNNING",
    targetUrl: "https://clerk.com",
    createdAt: new Date().toISOString(),
    taskPrompt: "Analyze the developer signup flow.",
  },
  {
    id: "run-3",
    name: "Analyze Stripe Pricing",
    status: "COMPLETED",
    targetUrl: "https://stripe.com",
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    taskPrompt: "Find the enterprise pricing details.",
  },
  {
    id: "run-4",
    name: "Scrape GitHub Homepage",
    status: "FAILED",
    targetUrl: "https://github.com",
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    taskPrompt: "Extract all repository links.",
  },
];

export default function RunDetailPage() {
  const params = useParams();
  const runId = params.runId as string;

  const [runDetails, setRunDetails] = useState<AgentRun | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // --- DATA FETCHING LOGIC ---
    // In a real app, you would fetch this data from your backend API
    // GET /api/v1/agent/run/{runId}
    const fetchRunDetails = () => {
      setIsLoading(true);
      // Simulate API call
      setTimeout(() => {
        const foundRun = mockAgentRuns.find((run) => run.id === runId);
        if (foundRun) {
          setRunDetails(foundRun);
          // Simulate initial logs
          setAgentLogs([
            `[INFO] Loading logs for run: ${foundRun.name}`,
            `[STATUS] Current status: ${foundRun.status}`,
          ]);
        }
        setIsLoading(false);
      }, 500);
    };

    if (runId) {
      fetchRunDetails();
    }
  }, [runId]);

  useEffect(() => {
    // --- WEBSOCKET LOGIC ---
    // This is where you would connect to your WebSocket to stream live logs
    // for the specific runId.
    if (runDetails && runDetails.status === "RUNNING") {
      const interval = setInterval(() => {
        setAgentLogs((prev) => [
          ...prev,
          `[LOG] Agent is performing an action...`,
        ]);
      }, 2000);

      return () => clearInterval(interval); // Cleanup on component unmount
    }
  }, [runDetails]);

  useEffect(() => {
    // Auto-scroll logs
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop =
        logsContainerRef.current.scrollHeight;
    }
  }, [agentLogs]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!runDetails) {
    return (
      <div className="flex h-full items-center justify-center text-center">
        <div>
          <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
          <h2 className="mt-4 text-xl font-semibold">Run Not Found</h2>
          <p className="text-muted-foreground">
            The agent run with ID '{runId}' could not be found.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 h-full p-4 sm:p-6 lg:p-8">
      {/* --- Live Agent View --- */}
      <Card className="lg:col-span-5 h-full flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Live Agent View</CardTitle>
          <div className="flex items-center gap-2">
            {runDetails.status === "RUNNING" && (
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
            )}
            <span className="text-sm text-muted-foreground">
              Status: {runDetails.status}
            </span>
          </div>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center p-2 bg-black rounded-b-lg">
          {runDetails.status === "RUNNING" ? (
            <img
              // This now correctly points to the MJPEG stream for the specific runId
              src={`http://localhost:8000/api/v1/agent/stream/${runId}`}
              alt={`Live view for ${runDetails.name}`}
              className="w-full h-full object-contain"
            />
          ) : (
            <div className="text-center text-muted-foreground p-8">
              <BotMessageSquare className="mx-auto h-12 w-12 mb-4" />
              <h3 className="text-lg font-semibold">Mission Concluded</h3>
              <p>
                This agent run has {runDetails.status.toLowerCase()}. The live
                view is no longer active.
              </p>
              {/* In a real app, you might show a final screenshot or a "Replay" button here */}
            </div>
          )}
        </CardContent>
      </Card>

      {/* --- Mission Log Panel --- */}
      <Card className="lg:col-span-2 flex flex-col h-full">
        <CardHeader>
          <CardTitle>Mission Log</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 flex-1">
          <div className="text-sm space-y-1 border-b pb-4">
            <p>
              <strong className="font-semibold">Target:</strong>{" "}
              <span className="font-mono text-muted-foreground break-all">
                {runDetails.targetUrl}
              </span>
            </p>
            <p>
              <strong className="font-semibold">Objective:</strong>{" "}
              <span className="text-muted-foreground">
                {runDetails.taskPrompt}
              </span>
            </p>
          </div>
          <div
            ref={logsContainerRef}
            className="flex-1 bg-muted rounded-md p-4 overflow-y-auto text-sm font-mono whitespace-pre-wrap border"
          >
            {agentLogs.join("\n")}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
