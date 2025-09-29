"use client";

import {
  TestimonialsColumn,
  Testimonial,
} from "@/components/landing/testimonials-columns-1";
import { motion } from "framer-motion";

const testimonials: Testimonial[] = [
  {
    text: "Churninator's report showed us exactly where users were dropping off in our competitor's signup flow. We redesigned our own based on those insights and boosted conversions by 15%.",
    image: "https://randomuser.me/api/portraits/women/12.jpg",
    name: "Sarah Johnson",
    role: "Product Manager, TechCorp",
  },
  {
    text: "Watching the AI agent navigate a rival's app in real-time is like having a superpower. It's the most honest, unbiased user test you could ever ask for.",
    image: "https://randomuser.me/api/portraits/men/34.jpg",
    name: "David Chen",
    role: "UX Researcher, Innovate Inc.",
  },
  {
    text: "As a founder, I don't have time for manual competitive analysis. Churninator automates the entire process and delivers an actionable report. It's a game-changer.",
    image: "https://randomuser.me/api/portraits/women/45.jpg",
    name: "Emily Rodriguez",
    role: "Founder, SaaS Solutions",
  },
  {
    text: "The AI-generated mockups are brilliant. It doesn't just point out a problem; it shows you a potential solution. This saved our design team hours of work.",
    image: "https://randomuser.me/api/portraits/men/56.jpg",
    name: "Michael Brown",
    role: "Head of Design, Creative Co.",
  },
  {
    text: "We thought our onboarding was smooth until Churninator analyzed our top 3 competitors. The report gave us a clear roadmap of quick wins to improve user activation.",
    image: "https://randomuser.me/api/portraits/women/67.jpg",
    name: "Jessica Williams",
    role: "Growth Marketer, ScaleUp",
  },
  {
    text: "It's one thing to read about UX best practices. It's another to see an AI physically struggle with a confusing UI on a competitor's site. The insights are visceral and unforgettable.",
    image: "https://randomuser.me/api/portraits/men/78.jpg",
    name: "Chris Martinez",
    role: "Frontend Developer, DevWorks",
  },
  {
    text: "The level of detail is insane. It pinpointed a confusing label in a dropdown that we never would have caught. This tool goes beyond simple screen recording.",
    image: "https://randomuser.me/api/portraits/women/89.jpg",
    name: "Amanda Garcia",
    role: "QA Engineer, LogicFlow",
  },
  {
    text: "We used Churninator to prep for our Series A pitch. Being able to show investors a data-backed analysis of our competitor's weaknesses was incredibly powerful.",
    image: "https://randomuser.me/api/portraits/men/90.jpg",
    name: "James Taylor",
    role: "Co-Founder & CEO, NextGen AI",
  },
  {
    text: "This is the future of market research. Raw, unfiltered, and automated. It's an essential part of our quarterly planning now.",
    image: "https://randomuser.me/api/portraits/women/23.jpg",
    name: "Linda Wilson",
    role: "VP of Product, Visionary",
  },
];

const firstColumn = testimonials.slice(0, 3);
const secondColumn = testimonials.slice(3, 6);
const thirdColumn = testimonials.slice(6, 9);

export function Testimonials() {
  return (
    <section className="bg-background py-16 md:py-32 relative">
      <div className="container z-10 mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: "easeInOut" }}
          viewport={{ once: true }}
          className="flex flex-col items-center justify-center max-w-2xl mx-auto text-center"
        >
          <h2 className="text-4xl font-semibold tracking-tight md:text-5xl">
            Trusted by the Teams That Win
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            See how product managers, founders, and designers are gaining an
            unfair advantage with Churninator.
          </p>
        </motion.div>

        <div className="relative flex justify-center gap-6 mt-12 [mask-image:linear-gradient(to_bottom,transparent,black_15%,black_85%,transparent)] max-h-[800px] overflow-hidden">
          <TestimonialsColumn testimonials={firstColumn} duration={25} />
          <TestimonialsColumn
            testimonials={secondColumn}
            className="hidden md:block"
            duration={30}
          />
          <TestimonialsColumn
            testimonials={thirdColumn}
            className="hidden lg:block"
            duration={28}
          />
        </div>
      </div>
    </section>
  );
}
