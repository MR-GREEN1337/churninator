"use client";

import { useSession } from "next-auth/react";
import { redirect } from "next/navigation";
import { ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { BrandPanel } from "@/components/auth/brand-panel"; // Import the new component

export default function AuthLayout({ children }: { children: ReactNode }) {
  const { status } = useSession();

  if (status === "authenticated") {
    redirect("/dashboard");
  }

  if (status === "loading") {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <main className="flex min-h-screen w-full bg-background">
      {/* Left Panel: The Auth Form */}
      <div className="flex w-full items-center justify-center p-8 lg:w-1/2">
        {children}
      </div>

      {/* Right Panel: The new animated branding */}
      <BrandPanel />
    </main>
  );
}
