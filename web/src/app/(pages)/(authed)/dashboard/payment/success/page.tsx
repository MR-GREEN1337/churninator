"use client";

import { useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import confetti from "canvas-confetti";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { CheckCircle2, ArrowRight, Loader2 } from "lucide-react";
import { useSWRConfig } from "swr";

function SuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const { mutate } = useSWRConfig();

  useEffect(() => {
    // Trigger confetti on successful load
    confetti({
      particleCount: 150,
      spread: 70,
      origin: { y: 0.6 },
      colors: ["#6366f1", "#a78bfa", "#f472b6"],
    });

    // Invalidate the user cache to refetch their subscription status
    if (sessionId) {
      mutate("/users/me");
    }
  }, [sessionId, mutate]);

  return (
    <div className="flex h-full items-center justify-center bg-gray-50/50 dark:bg-gray-900/50 p-4">
      <Card className="max-w-md w-full text-center shadow-2xl shadow-primary/10">
        <CardHeader className="items-center">
          <div className="p-4 bg-green-100 dark:bg-green-900/50 rounded-full">
            <CheckCircle2 className="h-10 w-10 text-green-500" />
          </div>
          <CardTitle className="text-3xl font-bold mt-4">
            Upgrade Complete!
          </CardTitle>
          <CardDescription className="text-lg text-muted-foreground pt-2">
            Welcome to Churninator Pro. Your new capabilities are now unlocked.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="mb-6">
            You're all set to gain an unfair advantage. What will you uncover
            first?
          </p>
          <Button asChild size="lg" className="w-full group">
            <Link href="/dashboard">
              Start Your First Pro Mission
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </Button>
          <p className="text-xs text-muted-foreground mt-4">
            A receipt has been sent to your email. You can manage your
            subscription in the billing settings.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

// Wrap with Suspense for useSearchParams
export default function SuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      }
    >
      <SuccessContent />
    </Suspense>
  );
}
