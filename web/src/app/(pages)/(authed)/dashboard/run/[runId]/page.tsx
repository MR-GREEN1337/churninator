"use client";

import { useEffect, useMemo, useRef } from "react";
import { useParams } from "next/navigation";
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { AgentRun } from "@/types";
import { useEventSource } from "@/hooks/use-event-source";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Loader2,
  BotMessageSquare,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from "lucide-react";

// --- Type Definitions for Final Report ---
interface FrictionPoint {
  step: number;
  screenshot_path: string;
  description: string;
  recommendation: string;
}

interface FinalReport {
  summary: string;
  positive_points: string[];
  friction_points: FrictionPoint[];
}

// --- Report Display Sub-Component ---
function FinalReportDisplay({
  report,
  runId,
}: {
  report: FinalReport;
  runId: string;
}) {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;

  return (
    <div className="lg:col-span-7 space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <CardTitle>AI-Powered Friction Report</CardTitle>
          </div>
          <CardDescription>{report.summary}</CardDescription>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h3 className="font-semibold flex items-center gap-2 text-lg">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              What Went Well
            </h3>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              {report.positive_points.map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <h3 className="font-semibold flex items-center gap-2 text-lg">
              <AlertCircle className="h-5 w-5 text-destructive" />
              Key Friction Points
            </h3>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              {report.friction_points.map((point) => (
                <AccordionItem value={`item-${point.step}`} key={point.step}>
                  <AccordionTrigger>
                    Step {point.step}: {point.description.substring(0, 60)}...
                  </AccordionTrigger>
                  <AccordionContent className="space-y-4 pt-2">
                    <div className="rounded-lg overflow-hidden border">
                      <img
                        src={`${apiBaseUrl}/agent/runs/${runId}/screenshots/${point.screenshot_path
                          .split("/")
                          .pop()}`}
                        alt={`Screenshot for step ${point.step}`}
                        className="w-full h-auto object-contain"
                      />
                    </div>
                    <div>
                      <h4 className="font-semibold text-foreground">
                        Issue Description
                      </h4>
                      <p className="text-muted-foreground text-sm">
                        {point.description}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-foreground">
                        Our Recommendation
                      </h4>
                      <p className="text-muted-foreground text-sm">
                        {point.recommendation}
                      </p>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// --- Main Page Component ---
export default function RunDetailPage() {
  const params = useParams();
  const runId = params.runId as string;

  const {
    data: runDetails,
    isLoading,
    error,
  } = useSWR<AgentRun>(runId ? `/agent/runs/${runId}` : null, fetcher, {
    refreshInterval: (latestData) =>
      latestData?.status === "COMPLETED" || latestData?.status === "FAILED"
        ? 0
        : 2000,
  });

  const logStreamUrl = useMemo(() => {
    if (!runId || !process.env.NEXT_PUBLIC_API_URL) return null;
    return `${process.env.NEXT_PUBLIC_API_URL}/agent/logs/${runId}`;
  }, [runId]);

  const agentLogs = useEventSource(logStreamUrl);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop =
        logsContainerRef.current.scrollHeight;
    }
  }, [agentLogs]);

  if (isLoading && !runDetails) {
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

  if (error || !runDetails) {
    return (
      <div className="flex h-full items-center justify-center text-center p-4">
        <div>
          <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
          <h2 className="mt-4 text-xl font-semibold">Run Not Found</h2>
          <p className="text-muted-foreground">
            The agent run with ID '{runId}' could not be found or you don't have
            permission to view it.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-7 h-full p-4 sm:p-6 lg:p-8">
      {(runDetails as any)?.final_result ? (
        <FinalReportDisplay
          report={(runDetails as any).final_result as FinalReport}
          runId={runId}
        />
      ) : (
        <>
          <Card className="lg:col-span-5 h-full flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Live Agent View</CardTitle>
              <div className="flex items-center gap-2">
                {((runDetails as any).status === "RUNNING" ||
                  (runDetails as any).status === "PENDING" ||
                  (runDetails as any).status === "ANALYZING") && (
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                )}
                <span className="text-sm text-muted-foreground capitalize">
                  {(runDetails as any).status.toLowerCase()}
                </span>
              </div>
            </CardHeader>
            <CardContent className="flex-1 flex items-center justify-center p-2 bg-black rounded-b-lg">
              {(runDetails as any).status === "ANALYZING" ? (
                <div className="text-center text-primary-foreground p-8">
                  <Sparkles className="mx-auto h-12 w-12 mb-4 animate-pulse text-primary" />
                  <h3 className="text-lg font-semibold">
                    Generating AI Report...
                  </h3>
                  <p className="text-muted-foreground">
                    The agent has finished its run. Our AI is now analyzing the
                    results to build your Friction Report. This can take a few
                    minutes.
                  </p>
                </div>
              ) : runDetails.status === "RUNNING" ||
                runDetails.status === "PENDING" ? (
                <img
                  src={`${process.env.NEXT_PUBLIC_API_URL}/agent/stream/${runId}`}
                  alt={`Live view for ${runDetails.task_prompt}`}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="text-center text-muted-foreground p-8">
                  <BotMessageSquare className="mx-auto h-12 w-12 mb-4" />
                  <h3 className="text-lg font-semibold">Mission Concluded</h3>
                  <p>
                    This agent run has {runDetails.status.toLowerCase()}. The
                    live view is no longer active.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="lg:col-span-2 flex flex-col h-full">
            <CardHeader>
              <CardTitle>Mission Log</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col gap-4 min-h-0">
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
                {agentLogs.length > 1
                  ? agentLogs.join("\n")
                  : "Waiting for log stream..."}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
