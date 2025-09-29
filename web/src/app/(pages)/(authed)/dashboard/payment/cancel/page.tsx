"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { XCircle, ArrowLeft, DollarSign } from "lucide-react";

export default function CancelPage() {
  return (
    <div className="flex h-full items-center justify-center bg-gray-50/50 dark:bg-gray-900/50 p-4">
      <Card className="max-w-md w-full text-center shadow-lg">
        <CardHeader className="items-center">
          <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-full">
            <XCircle className="h-10 w-10 text-muted-foreground" />
          </div>
          <CardTitle className="text-3xl font-bold mt-4">
            Checkout Canceled
          </CardTitle>
          <CardDescription className="text-lg text-muted-foreground pt-2">
            Your upgrade was not completed.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="mb-6">
            No problem at all. Your current plan remains unchanged. If you have
            any questions or feedback, we're here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Button asChild size="lg" variant="outline" className="w-full">
              <Link href="/#pricing">
                <DollarSign className="mr-2 h-4 w-4" /> View Pricing Plans
              </Link>
            </Button>
            <Button asChild size="lg" className="w-full">
              <Link href="/dashboard">
                <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
