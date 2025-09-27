// web/src/app/(pages)/(authed)/dashboard/run/[runId]/page.tsx
"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, BotMessageSquare, AlertTriangle } from "lucide-react";
import { useParams } from "next/navigation";
import { useAgentRun } from "@/hooks/use-agent-runs"; // LIVE DATA HOOK
import { Skeleton } from "@/components/ui/skeleton"; // LOADING STATE UI

export default function RunDetailPage() {
  const params = useParams();
  const runId = params.runId as string;

  // Use our SWR hook to fetch live data for this specific run
  const { run: runDetails, isLoading, isError } = useAgentRun(runId);

  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // --- WEBSOCKET LOGIC (Remains the same) ---
    // Connect to your WebSocket to stream live logs for the specific runId.
    if (
      runDetails &&
      (runDetails.status === "RUNNING" || runDetails.status === "PENDING")
    ) {
      // Replace this with your actual WebSocket connection
      // e.g., const ws = new WebSocket(`ws://localhost:8000/ws/logs/${runId}`);
      // ws.onmessage = (event) => setAgentLogs(prev => [...prev, event.data]);

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
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 h-full p-4 sm:p-6 lg:p-8">
        <Card className="lg:col-span-5 h-full flex flex-col">
          <CardHeader>
            <Skeleton className="h-8 w-1/3" />
          </CardHeader>
          <CardContent className="flex-1">
            <Skeleton className="h-full w-full" />
          </CardContent>
        </Card>
        <Card className="lg:col-span-2 flex flex-col h-full">
          <CardHeader>
            <Skeleton className="h-8 w-1/2" />
          </CardHeader>
          <CardContent className="flex flex-col gap-4 flex-1">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-full w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isError || !runDetails) {
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
            {(runDetails.status === "RUNNING" ||
              runDetails.status === "PENDING") && (
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
            )}
            <span className="text-sm text-muted-foreground capitalize">
              Status: {runDetails.status.toLowerCase()}
            </span>
          </div>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center p-2 bg-black rounded-b-lg">
          {runDetails.status === "RUNNING" ||
          runDetails.status === "PENDING" ? (
            <img
              // In a real app, this would point to your MJPEG stream
              // src={`http://localhost:8000/api/v1/agent/stream/${runId}`}
              src="https://placehold.co/1920x1080/000000/FFF?text=Live+Agent+View"
              alt={`Live view for ${runDetails.task_prompt}`}
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
                {runDetails.target_url}
              </span>
            </p>
            <p>
              <strong className="font-semibold">Objective:</strong>{" "}
              <span className="text-muted-foreground">
                {runDetails.task_prompt}
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
