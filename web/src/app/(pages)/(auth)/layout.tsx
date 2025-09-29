"use client";

import { useSession } from "next-auth/react";
import { redirect } from "next/navigation";
import { ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { BrandPanel } from "@/components/auth/brand-panel";
import { Logo } from "@/components/shared/logo";
import { ThemeToggle } from "@/components/theme-toggle";

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
      <div className="relative flex w-full items-center justify-center p-8 lg:w-1/2">
        <div className="absolute top-8 left-8">
          <Logo hideText={false} />
        </div>
        <div className="absolute top-8 right-8">
          <ThemeToggle isCollapsed={true} />
        </div>
        {children}
      </div>

      {/* Right Panel: The new animated branding */}
      <BrandPanel />
    </main>
  );
}
