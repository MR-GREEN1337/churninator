export interface AgentRun {
  id: string; // uuid.UUID is a string
  target_url: string;
  task_prompt: string;
  favicon_url: string | null;
  status: "PENDING" | "ANALYZING" | "RUNNING" | "COMPLETED" | "FAILED";
  report_path: string | null;
  run_log: string | null;
  final_result: FinalReport | null;
  created_at: string; // datetime is serialized as an ISO string
}

// Mirrors the UserRead Pydantic model
export interface User {
  id: string;
  email: string;
  is_active: boolean;
  full_name: string | null;
  // --- ADDED ---
  subscription_status?: "active" | "canceled" | "past_due" | null;
}

interface FrictionPoint {
  step: number;
  screenshot_path: string;
  description: string;
  recommendation: string;
}

export interface FinalReport {
  summary: string;
  positive_points: string[];
  friction_points: FrictionPoint[];
}
