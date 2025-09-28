"use client";

import { useSession } from "next-auth/react";
import { redirect } from "next/navigation";
import { ReactNode } from "react";
import { Loader2 } from "lucide-react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  const { status } = useSession();

  // If the user is already authenticated, redirect them to the dashboard.
  if (status === "authenticated") {
    redirect("/dashboard");
  }

  // While the session is loading, show a spinner.
  if (status === "loading") {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  // If unauthenticated, render the login/signup pages.
  return <>{children}</>;
}
