// web/src/components/landing/hero.tsx
import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AnimatedGroup } from "@/components/ui/animated-group"; // Assuming this is a custom animation component
import { HeaderClient } from "./header-client";
import { UserButton } from "../auth/user-button";
import { ThemeToggle } from "../theme-toggle";
// You will need to create UserButton, HeaderClient, and ThemeToggle components
// import { UserButton } from "../auth/user-button";
// import { HeaderClient } from "./header-client";
// import { ThemeToggle } from "../theme-toggle";

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

export function HeroSection() {
  return (
    <>
      <HeroHeader />
      <main className="overflow-hidden">
        {/* Decorative background gradients */}
        <div
          aria-hidden
          className="z-[2] absolute inset-0 pointer-events-none isolate opacity-50 contain-strict hidden lg:block"
        >
          <div className="w-[35rem] h-[80rem] -translate-y-[350px] absolute left-0 top-0 -rotate-45 rounded-full bg-[radial-gradient(68.54%_68.72%_at_55.02%_31.46%,hsl(var(--primary)/.08)_0,hsl(var(--primary)/.02)_50%,transparent_80%)]" />
        </div>
        <section id="home" className="relative">
          {/* Grid background */}
          <div
            aria-hidden
            className="absolute inset-0 z-0 size-full bg-[linear-gradient(to_right,rgba(115,115,115,0.15)_1px,transparent_1px),linear-gradient(to_bottom,rgba(115,115,115,0.15)_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]"
          />

          {/* Content Layer */}
          <div className="relative z-10 pt-16 md:pt-32">
            <div className="mx-auto max-w-7xl px-6">
              <div className="text-center">
                {/* @ts-ignore */}
                <AnimatedGroup variants={transitionVariants}>
                  <Link
                    href="/#features"
                    className="hover:bg-background dark:hover:border-t-border bg-muted group mx-auto flex w-fit items-center gap-4 rounded-full border p-1 pl-4 shadow-md shadow-black/5 transition-all duration-300 dark:border-t-white/5 dark:shadow-zinc-950"
                  >
                    <span className="text-foreground text-sm">
                      Now Open Source: The AI-Powered Mystery Shopper
                    </span>
                    <span className="dark:border-background block h-4 w-0.5 border-l bg-white dark:bg-zinc-700"></span>
                    <div className="bg-background group-hover:bg-muted size-6 overflow-hidden rounded-full duration-500">
                      <div className="flex w-12 -translate-x-1/2 duration-500 ease-in-out group-hover:translate-x-0">
                        <span className="flex size-6">
                          <ArrowRight className="m-auto size-3" />
                        </span>
                        <span className="flex size-6">
                          <ArrowRight className="m-auto size-3" />
                        </span>
                      </div>
                    </div>
                  </Link>

                  <h1 className="mt-10 max-w-4xl mx-auto text-balance text-6xl font-light tracking-tight md:text-7xl lg:mt-16 xl:text-[5.25rem] md:leading-tight">
                    Find and Eliminate Churn. Before it happens.
                  </h1>
                  <p className="mx-auto mt-8 max-w-2xl text-balance text-lg leading-relaxed text-muted-foreground">
                    Deploy an autonomous AI agent to mystery shop your
                    competitors' onboarding flows. Uncover friction points and
                    conversion killers with a level of detail humans can't
                    match.
                  </p>
                </AnimatedGroup>

                <AnimatedGroup
                  //@ts-ignore
                  variants={{
                    container: {
                      visible: {
                        transition: {
                          staggerChildren: 0.05,
                          delayChildren: 0.75,
                        },
                      },
                    },
                    ...transitionVariants,
                  }}
                  className="mt-12 flex flex-col items-center justify-center gap-2 md:flex-row"
                >
                  <Button asChild size="lg">
                    <Link href="/dashboard">
                      <span className="text-nowrap">Launch an Agent Now</span>
                    </Link>
                  </Button>
                  <Button asChild size="lg" variant="ghost">
                    <Link href="/#features">
                      <span className="text-nowrap">See How It Works</span>
                    </Link>
                  </Button>
                </AnimatedGroup>
              </div>
            </div>
            {/* Animated Screenshot */}
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
                  {/* Replace this with an image of your Churninator dashboard */}
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
    </>
  );
}

const menuItems = [
  { name: "Home", href: "#home", id: "home" },
  { name: "Features", href: "#features", id: "features" },
  { name: "Pricing", href: "#pricing", id: "pricing" },
  {
    name: "GitHub",
    href: "https://github.com/MR-GREEN1337/churninator",
    id: "github",
    withArrow: true,
  },
];

async function HeroHeader() {
  return (
    <header>
      <HeaderClient menuItems={menuItems}>
        <Button asChild variant="outline" size="sm">
          <Link href="#">Join Discord</Link>
        </Button>
        <UserButton />
        <ThemeToggle isCollapsed />
      </HeaderClient>
    </header>
  );
}
