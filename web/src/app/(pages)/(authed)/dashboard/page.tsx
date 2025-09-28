"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowRight, Globe, Loader2, SquareTerminal } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { toast } from "sonner";

// Mock suggestions, in a real app this would come from user history
const suggestions = [
  "https://github.com/login",
  "https://vercel.com",
  "https://clerk.com/pricing",
];

export default function DashboardPage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [prompt, setPrompt] = useState(
    "Perform a full analysis of the user onboarding flow.",
  );
  const [isLoading, setIsLoading] = useState(false);

  const handleLaunchAgent = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!url) {
      toast.error("Please enter a target URL.");
      return;
    }
    try {
      // Basic URL validation
      new URL(url);
    } catch (error) {
      toast.error("Please enter a valid URL.");
      return;
    }

    setIsLoading(true);

    try {
      const newRun = await api.createAgentRun({
        target_url: url,
        task_prompt: prompt,
      });

      toast.success(`Agent mission #${newRun.id.substring(0, 8)} is live!`);

      router.push(`/dashboard/run/${newRun.id}`);
    } catch (error: any) {
      console.error("Failed to launch agent:", error);
      toast.error("Failed to launch agent.", {
        description: error.message || "Please try again later.",
      });
      setIsLoading(false);
    }
  };

  return (
    // --- START FIX ---
    // The `h-full` property ensures this div takes up the full height of the main content area.
    // `flex items-center justify-center` will then perfectly center the child div.
    <div className="flex h-full items-center justify-center">
      {/* --- END FIX --- */}
      <motion.div
        key="idle"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="w-full max-w-2xl text-center p-4"
      >
        <SquareTerminal className="mx-auto h-12 w-12 text-primary mb-4" />
        <h1 className="text-4xl font-bold tracking-tight mb-2">
          Churninator Command Center
        </h1>
        <p className="text-muted-foreground mb-8">
          Enter a target URL and a task to begin your reconnaissance mission.
        </p>

        <form onSubmit={handleLaunchAgent}>
          <div className="relative">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://competitor.com/signup"
              className="pl-10 h-14 text-lg rounded-full shadow-lg"
              disabled={isLoading}
            />
            <Button
              type="submit"
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full"
              disabled={!url || isLoading}
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <ArrowRight className="h-5 w-5" />
              )}
            </Button>
          </div>
        </form>

        <div className="mt-4 flex flex-wrap justify-center gap-2">
          <span className="text-sm text-muted-foreground mr-2">Try:</span>
          {suggestions.map((s) => (
            <Button
              key={s}
              variant="outline"
              size="sm"
              className="rounded-full"
              onClick={() => setUrl(s)}
              disabled={isLoading}
            >
              {s}
            </Button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
