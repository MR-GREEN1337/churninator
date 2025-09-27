// web/src/hooks/use-agent-runs.ts
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { AgentRun } from "@/types";

export function useAgentRuns() {
  const { data, error, isLoading, mutate } = useSWR<AgentRun[]>(
    "/agent/runs",
    fetcher,
  );

  return {
    runs: data,
    isLoading,
    isError: error,
    mutate,
  };
}

export function useAgentRun(runId: string | null) {
  const { data, error, isLoading, mutate } = useSWR<AgentRun>(
    // The key is the URL. If runId is null, SWR won't start the request.
    runId ? `/agent/runs/${runId}` : null,
    fetcher,
  );

  return {
    run: data,
    isLoading,
    isError: error,
    mutate,
  };
}
