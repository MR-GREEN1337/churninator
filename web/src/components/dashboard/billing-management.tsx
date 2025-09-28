"use client";

import { useState } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loader2 } from "lucide-react";

export function BillingManagement() {
  const [isRedirecting, setIsRedirecting] = useState(false);

  const handleManageSubscription = async () => {
    setIsRedirecting(true);
    try {
      const { url } = await api.createPortalSession();
      window.location.href = url;
    } catch (error) {
      toast.error("Could not redirect to billing portal. Please try again.");
      setIsRedirecting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Subscription</CardTitle>
        <CardDescription>
          You are on the **Churninator Pro** plan. Manage your subscription and
          view payment history in the Stripe customer portal.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button onClick={handleManageSubscription} disabled={isRedirecting}>
          {isRedirecting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Manage Billing & Subscription
        </Button>
      </CardContent>
    </Card>
  );
}
