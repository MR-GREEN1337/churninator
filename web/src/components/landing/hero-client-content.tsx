"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowRight, Loader2, SquareTerminal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AnimatedGroup } from "@/components/ui/animated-group";
import { useMediaQuery } from "@/hooks/use-media-query";
import { useScroll } from "framer-motion";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { FlickeringGrid } from "./flickering-grid";

const transitionVariants = {
  item: {
    hidden: { opacity: 0, filter: "blur(12px)", y: 12 },
    visible: {
      opacity: 1,
      filter: "blur(0px)",
      y: 0,
      transition: { type: "spring", bounce: 0.3, duration: 1.5 },
    },
  },
};

// Mock suggestions, same as dashboard
const suggestions = [
  "https://github.com/login",
  "https://vercel.com",
  "https://clerk.com/pricing",
];

export function HeroClientContent() {
  const tablet = useMediaQuery("(max-width: 1024px)");
  const [mounted, setMounted] = useState(false);
  const [isScrolling, setIsScrolling] = useState(false);
  const scrollTimeout = useRef<NodeJS.Timeout | null>(null);
  const { scrollY } = useScroll();

  // --- START: Added state and logic from dashboard ---
  const router = useRouter();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLaunchAgent = async (event: React.FormEvent) => {
    event.preventDefault();

    const urlMatch = input.match(/(https?:\/\/[^\s]+)/);
    const url = urlMatch ? urlMatch[0] : "";
    const prompt =
      input.replace(url, "").trim() ||
      "Perform a full analysis of the user onboarding flow.";

    if (!url) {
      toast.error("Please include a target URL in your input.");
      return;
    }

    try {
      new URL(url);
    } catch (error) {
      toast.error("Please enter a valid URL.");
      return;
    }

    setIsLoading(true);

    try {
      const newRun = await api.createAgentRun({
        target_url: url,
        task_prompt: prompt,
      });

      toast.success(`Agent mission #${newRun.id.substring(0, 8)} is live!`);
      router.push(`/dashboard/run/${newRun.id}`);
    } catch (error: any) {
      if (error.status === 401) {
        toast.error("Authentication Required", {
          description: "Please sign in to launch an agent.",
          action: {
            label: "Sign In",
            onClick: () => router.push("/login"),
          },
        });
      } else {
        toast.error("Failed to launch agent.", {
          description: error.message || "Please try again later.",
        });
      }
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (url: string) => {
    setInput(`Analyze the signup flow for ${url}`);
  };
  // --- END: Added state and logic from dashboard ---

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const unsubscribe = scrollY.on("change", () => {
      setIsScrolling(true);
      if (scrollTimeout.current) {
        clearTimeout(scrollTimeout.current);
      }
      scrollTimeout.current = setTimeout(() => {
        setIsScrolling(false);
      }, 300);
    });

    return () => {
      unsubscribe();
      if (scrollTimeout.current) {
        clearTimeout(scrollTimeout.current);
      }
    };
  }, [scrollY]);

  return (
    <main className="overflow-hidden">
      <div
        aria-hidden
        className="z-[2] absolute inset-0 pointer-events-none isolate opacity-50 contain-strict hidden lg:block"
      >
        <div className="w-[35rem] h-[80rem] -translate-y-[350px] absolute left-0 top-0 -rotate-45 rounded-full bg-[radial-gradient(68.54%_68.72%_at_55.02%_31.46%,hsl(var(--primary)/.08)_0,hsl(var(--primary)/.02)_50%,transparent_80%)]" />
      </div>
      <section id="home" className="relative">
        <div
          aria-hidden="true"
          className="absolute inset-0 z-0 size-full [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]"
        >
          <div className="absolute left-0 top-0 h-full w-1/3 -z-10 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-background z-10" />
            {mounted && (
              <FlickeringGrid
                className="h-full w-full"
                squareSize={tablet ? 1.5 : 2}
                gridGap={tablet ? 1.5 : 2}
                maxOpacity={tablet ? 0.1 : 0.2}
                flickerChance={isScrolling ? 0.005 : tablet ? 0.01 : 0.02}
              />
            )}
          </div>
          <div className="absolute right-0 top-0 h-full w-1/3 -z-10 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-l from-transparent via-transparent to-background z-10" />
            {mounted && (
              <FlickeringGrid
                className="h-full w-full"
                squareSize={tablet ? 1.5 : 2}
                gridGap={tablet ? 1.5 : 2}
                maxOpacity={tablet ? 0.1 : 0.2}
                flickerChance={isScrolling ? 0.005 : tablet ? 0.01 : 0.02}
              />
            )}
          </div>
        </div>

        <div className="relative z-10 pt-12 md:pt-24">
          <div className="mx-auto max-w-7xl px-6">
            <div className="text-center">
              {/* @ts-ignore */}
              <AnimatedGroup variants={transitionVariants}>
                <h1 className="mt-10 max-w-4xl mx-auto text-balance text-4xl font-light tracking-tight md:text-5xl lg:mt-16 xl:text-[5rem] md:leading-tight">
                  Find and Eliminate Churn. Before it happens.
                </h1>
                <p className="mx-auto mt-4 text-sm max-w-2xl text-balance text-lg leading-relaxed text-muted-foreground">
                  Deploy an autonomous AI agent to mystery shop your
                  competitors' onboarding flows. Uncover friction points and
                  conversion killers with a level of detail humans can't match.
                </p>
              </AnimatedGroup>

              {/* --- START: Replaced Buttons with Input Form --- */}
              <div className="mt-12 max-w-2xl mx-auto">
                <form onSubmit={handleLaunchAgent} className="space-y-4">
                  <div className="relative">
                    <SquareTerminal className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <Input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Analyze the signup flow for https://competitor.com/signup"
                      className="pl-10 pr-14 h-14 text-lg rounded-full shadow-lg"
                      disabled={isLoading}
                    />
                    <Button
                      type="submit"
                      size="icon"
                      className="absolute right-2 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full"
                      disabled={!input || isLoading}
                    >
                      {isLoading ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <ArrowRight className="h-5 w-5" />
                      )}
                    </Button>
                  </div>
                </form>

                <div className="mt-4 flex flex-wrap justify-center gap-2">
                  <span className="text-sm text-muted-foreground mr-2">
                    Try:
                  </span>
                  {suggestions.map((s) => (
                    <Button
                      key={s}
                      variant="outline"
                      size="sm"
                      className="rounded-full"
                      onClick={() => handleSuggestionClick(s)}
                      disabled={isLoading}
                    >
                      {s}
                    </Button>
                  ))}
                </div>
              </div>
              {/* --- END: Replaced Buttons with Input Form --- */}
            </div>
          </div>
          <AnimatedGroup
            //@ts-ignore
            variants={{
              container: {
                visible: {
                  transition: { staggerChildren: 0.05, delayChildren: 0.75 },
                },
              },
              ...transitionVariants,
            }}
          >
            <div className="relative mt-8 sm:mt-12 md:mt-20">
              <div
                aria-hidden
                className="bg-gradient-to-b to-background absolute inset-0 z-10 from-transparent from-35%"
              />
              <div className="inset-shadow-2xs ring-background dark:inset-shadow-white/20 bg-background relative mx-auto max-w-6xl overflow-hidden rounded-2xl border p-2 shadow-lg shadow-zinc-950/15 ring-1">
                <img
                  className="bg-background aspect-[1200/630] w-full relative rounded-xl"
                  src="/agent.png"
                  alt="Churninator Application Dashboard"
                  width="1200"
                  height="630"
                />
              </div>
            </div>
          </AnimatedGroup>
        </div>
      </section>
    </main>
  );
}
