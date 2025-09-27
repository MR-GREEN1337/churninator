import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function PricingSkeleton() {
  return (
    <div id="pricing" className="mx-auto max-w-7xl px-6 py-20">
      <div className="text-center space-y-4 mb-12">
        <Skeleton className="h-12 w-3/4 mx-auto" />
        <Skeleton className="h-6 w-1/2 mx-auto" />
      </div>

      <div className="flex justify-center items-center mb-10 space-x-3">
        <Skeleton className="h-6 w-20" />
        <Skeleton className="h-6 w-12 rounded-full" />
        <Skeleton className="h-6 w-32" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-0 pt-12">
        {[1, 2, 3].map((i) => (
          <Card
            key={i}
            className={cn(
              "p-8 relative flex flex-col",
              i === 2
                ? "border-primary/20 border-2 lg:scale-105 z-10 bg-background"
                : "border-border bg-background lg:scale-95",
            )}
          >
            <div className="flex-1 flex flex-col pt-4">
              <Skeleton className="h-5 w-24 mx-auto" />
              <Skeleton className="h-12 w-32 mx-auto mt-6" />
              <Skeleton className="h-4 w-20 mx-auto mt-2" />
              <div className="mt-8 space-y-3 flex-grow">
                {[...Array(5)].map((_, j) => (
                  <div key={j} className="flex items-start gap-3">
                    <Skeleton className="h-5 w-5 rounded-full mt-0.5 flex-shrink-0" />
                    <Skeleton className="h-5 w-full" />
                  </div>
                ))}
              </div>
            </div>
            <Skeleton className="h-12 w-full mt-8" />
            <Skeleton className="h-4 w-3/4 mx-auto mt-6" />
          </Card>
        ))}
      </div>
    </div>
  );
}
