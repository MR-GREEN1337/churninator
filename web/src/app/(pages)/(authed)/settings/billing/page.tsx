"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { User } from "@/types";
import { BillingManagement } from "@/components/dashboard/billing-management";
import { Skeleton } from "@/components/ui/skeleton";
import { redirect } from "next/navigation";

export default function BillingPage() {
  const { data: user, isLoading } = useSWR<User>("/users/me", fetcher);

  if (isLoading) {
    return (
      <div className="p-8">
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  // If user is subscribed, show management portal. Otherwise, show pricing.
  return (
    <div>
      {user?.subscription_status === "active" ? (
        <BillingManagement />
      ) : (
        redirect("/#pricing")
      )}
    </div>
  );
}
