// web/src/components/landing/features.tsx
import { Card, CardContent } from "@/components/ui/card";
import { Bot, FileText, LocateFixed, Zap } from "lucide-react"; // Changed icons

export function Features() {
  return (
    <section id="features" className="py-16 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-4xl font-semibold tracking-tight md:text-5xl">
            A Machine's Eye for User Friction
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Churninator provides two core functions. A live feed to observe the
            agent in real-time, and a detailed final report to analyze its
            findings.
          </p>
        </div>
        <div className="relative mt-12">
          <div className="relative z-10 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card className="relative col-span-1 flex flex-col overflow-hidden p-2">
              <CardContent className="flex flex-1 flex-col items-center justify-center rounded-xl bg-background p-8 text-center">
                <div className="flex size-16 items-center justify-center rounded-full border bg-muted">
                  <LocateFixed
                    className="size-8 text-primary"
                    strokeWidth={1.5}
                  />
                </div>
                <h3 className="mt-6 text-2xl font-semibold">The Observatory</h3>
                <p className="mt-2 text-muted-foreground">
                  Watch the AI agent navigate your target's website in
                  real-time. See every click, scroll, and typed character
                  alongside the agent's "inner monologue," giving you an
                  unparalleled view of the user journey.
                </p>
              </CardContent>
            </Card>

            <Card className="relative col-span-1 flex flex-col overflow-hidden p-2">
              <CardContent className="flex flex-1 flex-col items-center justify-center rounded-xl bg-background p-8 text-center">
                <div className="flex size-16 items-center justify-center rounded-full border bg-muted">
                  <FileText className="size-8 text-primary" strokeWidth={1.5} />
                </div>
                <h3 className="mt-6 text-2xl font-semibold">
                  The Friction Report
                </h3>
                <p className="mt-2 text-muted-foreground">
                  After the mission, receive a detailed, step-by-step breakdown
                  of the entire onboarding flow. Instantly identify confusing
                  UI, dead ends, and moments of friction that cause users to
                  churn.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}
