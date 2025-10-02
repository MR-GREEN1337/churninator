"use client";

import { useEffect, useMemo, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { AgentRun, FinalReport } from "@/types";
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
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Loader2,
  BotMessageSquare,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  FileDown,
} from "lucide-react";

// --- Type Definitions for Final Report ---

// --- Report Display Sub-Component ---
function FinalReportDisplay({
  report,
  runDetails,
}: {
  report: FinalReport;
  runDetails: AgentRun;
}) {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
  const frictionScore = Math.max(10 - report.friction_points.length * 2, 1);

  return (
    <div className="lg:col-span-7 space-y-6">
      {/* Header Card with Key Metrics */}
      <Card className="overflow-hidden">
        <CardHeader className="flex flex-row items-start bg-muted/50">
          <div className="grid gap-0.5">
            <CardTitle className="group flex items-center gap-2 text-lg">
              <Sparkles className="h-5 w-5 text-primary" />
              AI Friction Report
            </CardTitle>
            <CardDescription>{report.summary}</CardDescription>
          </div>
          <div className="ml-auto flex items-center gap-2">
            {runDetails.report_path && (
              <Button asChild size="sm">
                <a
                  href={`${apiBaseUrl}/agent/runs/${runDetails.id}/report/download`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <FileDown className="mr-2 h-4 w-4" /> Download Report
                </a>
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-6 text-sm">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="flex flex-col gap-1">
              <div className="font-semibold text-muted-foreground">
                Friction Score
              </div>
              <div className="text-4xl font-bold">
                {frictionScore}
                <span className="text-2xl text-muted-foreground">/10</span>
              </div>
            </div>
            <div className="flex flex-col gap-1">
              <div className="font-semibold text-muted-foreground">
                Positive Points
              </div>
              <div className="text-4xl font-bold">
                {report.positive_points.length}
              </div>
            </div>
            <div className="flex flex-col gap-1">
              <div className="font-semibold text-muted-foreground">
                Friction Points
              </div>
              <div className="text-4xl font-bold text-destructive">
                {report.friction_points.length}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <h3 className="font-semibold flex items-center gap-2 text-lg">
                <CheckCircle2 className="h-5 w-5 text-green-500" /> What Went
                Well
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
        </div>
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <h3 className="font-semibold flex items-center gap-2 text-lg">
                <AlertCircle className="h-5 w-5 text-destructive" /> Key
                Friction Points & Recommendations
              </h3>
            </CardHeader>
            <CardContent>
              <Accordion type="single" collapsible className="w-full">
                {report.friction_points.map((point) => (
                  <AccordionItem value={`item-${point.step}`} key={point.step}>
                    <AccordionTrigger className="text-left">
                      Step {point.step}: {point.description.substring(0, 80)}...
                    </AccordionTrigger>
                    <AccordionContent className="space-y-4 pt-2">
                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle className="font-semibold">
                          Issue Description
                        </AlertTitle>
                        <AlertDescription>{point.description}</AlertDescription>
                      </Alert>
                      <Alert
                        variant="default"
                        className="bg-green-500/10 border-green-500/50 text-green-200"
                      >
                        <Sparkles className="h-4 w-4 text-green-500" />
                        <AlertTitle className="font-semibold text-green-400">
                          AI Recommendation
                        </AlertTitle>
                        <AlertDescription>
                          {point.recommendation}
                        </AlertDescription>
                      </Alert>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <h4 className="text-sm font-semibold text-center text-muted-foreground">
                            Before
                          </h4>
                          <img
                            src={`${apiBaseUrl}/agent/runs/${runDetails.id}/screenshots/step_${point.step}.jpeg`}
                            alt={`Before - Step ${point.step}`}
                            className="rounded-md border"
                          />
                        </div>
                        <div className="space-y-2">
                          <h4 className="text-sm font-semibold text-center text-muted-foreground">
                            AI Mockup (After)
                          </h4>
                          <img
                            src={`${apiBaseUrl}/agent/runs/${runDetails.id}/screenshots/after_${point.step}.png`}
                            alt={`After - Step ${point.step}`}
                            className="rounded-md border"
                          />
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>
        </div>
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
    refreshInterval: (data) =>
      data?.status === "COMPLETED" || data?.status === "FAILED" ? 0 : 3000,
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
      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-7 h-full p-4 sm:p-6 lg:p-8">
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
          <Button asChild className="mt-4">
            <Link href="/dashboard">Back to Dashboard</Link>
          </Button>
        </div>
      </div>
    );
  }

  // --- RENDER LOGIC ---
  return (
    <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-7 h-full p-4 sm:p-6 lg:p-8">
      {runDetails?.status === "COMPLETED" && runDetails.final_result ? (
        <FinalReportDisplay
          report={runDetails.final_result as FinalReport}
          runDetails={runDetails}
        />
      ) : (
        <>
          <Card className="lg:col-span-5 h-full flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Live Agent View</CardTitle>
              <Badge
                variant={
                  runDetails.status === "FAILED" ? "destructive" : "default"
                }
                className="capitalize flex items-center gap-2"
              >
                {(runDetails.status === "RUNNING" ||
                  runDetails.status === "PENDING" ||
                  runDetails.status === "ANALYZING") && (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )}
                {runDetails.status.toLowerCase()}
              </Badge>
            </CardHeader>
            <CardContent className="flex-1 flex items-center justify-center p-2 bg-black rounded-b-lg">
              {runDetails.status === "ANALYZING" ? (
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
                  <h3 className="text-lg font-semibold">
                    Mission{" "}
                    {runDetails.status === "FAILED" ? "Failed" : "Concluded"}
                  </h3>
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
