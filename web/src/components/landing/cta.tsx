import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function Cta() {
  return (
    <section className="relative py-20">
      <div
        aria-hidden="true"
        className="absolute inset-0 top-1/2 -z-10 h-1/2 w-full bg-background"
      />
      <div className="mx-auto max-w-5xl px-6">
        <div className="relative overflow-hidden rounded-2xl bg-primary/5 px-8 py-16 text-center shadow-lg dark:bg-primary/10 border border-primary/10">
          <div
            aria-hidden
            className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 opacity-20 dark:opacity-10"
          >
            <svg
              viewBox="0 0 40 40"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="h-full w-full text-primary"
            >
              <path
                d="M20 4L36 20L20 36L4 20Z"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M20 12V28M12 20H28"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Ready to master your next conversation?
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Stop leaving your success to chance. Start training with Recast
            today and turn insight into instinct.
          </p>
          <Button asChild size="lg" className="mt-8 group">
            <Link href="/signup">
              Get Started Now
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
