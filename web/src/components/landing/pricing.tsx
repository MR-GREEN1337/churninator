"use client";

import { Button, buttonVariants } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { useMediaQuery } from "@/hooks/use-media-query";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Check, Star, Loader2 } from "lucide-react";
import Link from "next/link";
import { useState, useRef, useTransition, useEffect } from "react"; // Import useEffect
import confetti from "canvas-confetti";
import NumberFlow from "@number-flow/react";
import { toast } from "sonner";
import { PricingSkeleton } from "./pricing-skeleton"; // Import the skeleton
import { url } from "inspector";
import { error } from "console";

const recastPlans = [
  {
    name: "ESSENTIAL",
    priceId: "",
    price: "19",
    yearlyPrice: "15",
    period: "per month",
    features: [
      "5 Conversation Analyses / month",
      "5 AI Sparring Sessions / month",
      "Standard Rhetorical Insights",
      "Secure & Private by Default",
      "Email Support",
    ],
    description: "For casual users sharpening their daily interactions",
    buttonText: "Choose Essential",
    isPopular: false,
  },
  {
    name: "PRO",
    priceId: "",
    price: "29",
    yearlyPrice: "23",
    period: "per month",
    features: [
      "Unlimited Analyses & Sparring",
      "Advanced Rhetorical Insights",
      "Power Dynamics Reporting",
      "Filler Word Detection",
      "Priority Email Support",
      "Access to All Future Updates",
    ],
    description: "For professionals committed to mastering communication",
    buttonText: "Get Started",
    isPopular: true,
  },
  {
    name: "TEAMS",
    priceId: null,
    price: "Custom",
    yearlyPrice: "Custom",
    period: " ",
    features: [
      "Everything in Pro",
      "Centralized Billing & Admin",
      "Team Performance Dashboards",
      "Custom Onboarding & Scenarios",
      "Dedicated Account Manager",
    ],
    description: "For organizations investing in their team's persuasive power",
    buttonText: "Contact Sales",
    isPopular: false,
  },
];

function CheckoutButton({
  priceId,
  buttonText,
  isPopular,
}: {
  priceId: string;
  buttonText: string;
  isPopular: boolean;
}) {
  const [isPending, startTransition] = useTransition();

  return (
    <button
      onClick={() => {}}
      disabled={isPending}
      className={cn(
        buttonVariants({
          variant: isPopular ? "default" : "outline",
          size: "lg",
        }),
        "w-full mt-8",
        isPending && "opacity-75 cursor-not-allowed",
      )}
    >
      {isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
      {isPending ? "Redirecting..." : buttonText}
    </button>
  );
}

// This contains the actual component logic.
function PricingContent() {
  const [isMonthly, setIsMonthly] = useState(true);
  const isDesktop = useMediaQuery("(min-width: 768px)");
  const switchRef = useRef<HTMLButtonElement>(null);

  const handleToggle = (checked: boolean) => {
    setIsMonthly(!checked);
    if (checked && switchRef.current) {
      const rect = switchRef.current.getBoundingClientRect();
      const x = rect.left + rect.width / 2;
      const y = rect.top + rect.height / 2;

      confetti({
        particleCount: 50,
        spread: 60,
        origin: {
          x: x / window.innerWidth,
          y: y / window.innerHeight,
        },
        colors: ["hsl(var(--primary))", "hsl(166 84% 50%)"],
        ticks: 200,
        gravity: 1.2,
        decay: 0.94,
        startVelocity: 30,
        shapes: ["circle"],
      });
    }
  };

  return (
    <div id="pricing" className="mx-auto max-w-7xl px-6 py-20">
      <div className="text-center space-y-4 mb-12">
        <h2 className="text-4xl font-bold tracking-tight sm:text-5xl">
          One Plan to Unlock Your Potential
        </h2>
        <p className="text-muted-foreground text-lg whitespace-pre-line">
          Become the most confident and persuasive person in the room.
          <br />
          Simple, transparent pricing. Cancel anytime.
        </p>
      </div>

      <div className="flex justify-center items-center mb-10 space-x-3">
        <span className="font-semibold">Monthly</span>
        <Switch
          ref={switchRef}
          checked={!isMonthly}
          onCheckedChange={handleToggle}
          aria-label="Toggle annual billing"
        />
        <span className="font-semibold">
          Annual <span className="text-primary">(Save 20%)</span>
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-0 pt-12">
        {recastPlans.map((plan) => {
          const isCustomPrice = isNaN(Number(plan.price));
          return (
            <motion.div
              key={plan.name}
              initial={{ y: 50, opacity: 0 }}
              whileInView={{
                y: plan.isPopular && isDesktop ? -20 : 0,
                opacity: 1,
              }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{
                duration: 0.8,
                type: "spring",
              }}
              className={cn(
                `rounded-2xl border p-8 text-center relative flex flex-col`,
                plan.isPopular
                  ? "border-primary border-2 lg:scale-105 z-10 bg-background"
                  : "border-border bg-background lg:scale-95",
              )}
            >
              {plan.isPopular && (
                <div className="absolute top-0 -translate-y-1/2 left-1/2 -translate-x-1/2">
                  <div className="bg-primary py-1 px-4 rounded-full flex items-center shadow-md">
                    <Star className="text-primary-foreground h-4 w-4 fill-current" />
                    <span className="text-primary-foreground ml-2 text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                </div>
              )}
              <div className="flex-1 flex flex-col pt-4">
                <p className="text-base font-semibold text-muted-foreground tracking-widest">
                  {plan.name}
                </p>
                <div className="mt-6 flex items-baseline justify-center gap-x-2">
                  {isCustomPrice ? (
                    <span className="text-5xl font-bold tracking-tight text-foreground">
                      {plan.price}
                    </span>
                  ) : (
                    <>
                      <span className="text-5xl font-bold tracking-tight text-foreground">
                        <NumberFlow
                          value={
                            isMonthly
                              ? Number(plan.price)
                              : Number(plan.yearlyPrice)
                          }
                          format={{
                            style: "currency",
                            currency: "USD",
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0,
                          }}
                          // @ts-ignore
                          formatter={(value: number) => `$${value}`}
                          className="font-sans"
                        />
                      </span>
                      <span className="text-sm font-semibold leading-6 tracking-wide text-muted-foreground">
                        {plan.period}
                      </span>
                    </>
                  )}
                </div>

                <p className="text-xs leading-5 text-muted-foreground">
                  {isCustomPrice
                    ? " "
                    : isMonthly
                      ? "billed monthly"
                      : "billed annually"}
                </p>

                <ul className="mt-8 space-y-3 flex-grow">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-left text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {plan.priceId ? (
                <CheckoutButton
                  priceId={plan.priceId}
                  buttonText={plan.buttonText}
                  isPopular={plan.isPopular}
                />
              ) : (
                <Button
                  asChild
                  size="lg"
                  className="w-full mt-8"
                  variant={plan.isPopular ? "default" : "outline"}
                >
                  <Link href="/contact-sales">{plan.buttonText}</Link>
                </Button>
              )}

              <p className="mt-6 text-xs leading-5 text-muted-foreground">
                {plan.description}
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

// This is the new default export that handles the mounted state.
export function Pricing() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return <PricingSkeleton />;
  }

  return <PricingContent />;
}
