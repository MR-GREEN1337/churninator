// web/src/components/landing/faq.tsx
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

// --- START TEXT UPDATE ---
const faqs = [
  {
    question: "Is this legal and will my agents get blocked?",
    answer:
      "Our agents are designed for ethical reconnaissance. They operate from standard residential IP pools and mimic human behavior to minimize detection, making them far more robust than traditional scrapers. While no automated system is 100% undetectable, we provide a powerful tool for competitive analysis. We advise using it responsibly and in accordance with the terms of service of the sites you analyze.",
  },
  {
    question: "What kind of websites can the agent analyze?",
    answer:
      "Any modern web application. Our agent is built on Playwright and powered by a Vision-Language Model, allowing it to navigate complex, dynamic user interfaces built with React, Vue, Svelte, and other JavaScript frameworks—just like a human would.",
  },
  {
    question: "How does the AI actually identify 'friction'?",
    answer:
      "The magic is in the model's 'inner monologue.' We've fine-tuned it not just to complete tasks, but to reason about its own actions. The final Friction Report highlights moments of confusion, repeated actions, and deviations from the optimal path, providing a qualitative map of a user's potential struggle.",
  },
  {
    question: "How is this different from tools like Hotjar or FullStory?",
    answer:
      "Those are fantastic tools for understanding users on YOUR OWN site. Churninator is a competitive intelligence tool designed to give you that same level of deep insight for ANY OTHER site on the internet. It's for analyzing your competitors, not your own customers.",
  },
  {
    question: "Is my data and the reports secure?",
    answer:
      "Absolutely. On our cloud platform, all agent runs and reports are encrypted and strictly isolated to your account. For maximum control, our Enterprise plan allows you to self-host the entire platform within your own infrastructure, ensuring no data ever leaves your environment.",
  },
];

export function Faq() {
  return (
    <section id="faq" className="py-16 md:py-32">
      <div className="mx-auto max-w-3xl px-6">
        <div className="text-center">
          <h2 className="text-4xl font-semibold tracking-tight md:text-5xl">
            Mission Briefing
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Key intelligence on how Churninator operates before you deploy your
            first agent.
          </p>
        </div>
        <div className="mt-12">
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem value={`item-${index}`} key={index}>
                <AccordionTrigger className="text-left text-lg">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-base text-muted-foreground">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  );
}
// --- END TEXT UPDATE ---
