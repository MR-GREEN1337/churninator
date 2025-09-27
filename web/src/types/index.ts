// Mirrors the AgentRunRead Pydantic model
export interface AgentRun {
  id: string; // uuid.UUID is a string
  target_url: string;
  task_prompt: string;
  favicon_url: string | null;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  created_at: string; // datetime is serialized as an ISO string
}

// Mirrors the UserRead Pydantic model
export interface User {
  id: string;
  email: string;
  is_active: boolean;
}
