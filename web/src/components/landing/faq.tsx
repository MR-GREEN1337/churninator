// web/src/components/landing/faq.tsx
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

// --- ADAPTED FAQs FOR CHURNINATOR ---
const faqs = [
  {
    question: "Is this legal and will my agents get blocked?",
    answer:
      "Churninator is a powerful reconnaissance tool. It uses advanced techniques to mimic human behavior, running from standard residential IP addresses to minimize detection. While no automated system is 100% undetectable, it is significantly more robust than traditional scrapers. We recommend using the tool responsibly and in accordance with the terms of service of the sites you analyze.",
  },
  {
    question: "What kind of websites can the agent analyze?",
    answer:
      "The agent is built on Playwright and powered by a Vision-Language Model, allowing it to navigate any modern web application, including those built with React, Vue, Svelte, and other JavaScript frameworks. It's designed to handle complex, dynamic user interfaces just like a human would.",
  },
  {
    question: "How does the AI actually identify 'friction'?",
    answer:
      "Our fine-tuned AGUVIS-style model is trained not just to complete tasks, but to generate an 'inner monologue' about its process. It identifies friction by reasoning about its own actions. The final report highlights moments of confusion, repeated actions, deviations from an optimal path, and long pauses, providing a qualitative map of the user's struggle.",
  },
  {
    question: "Can I run the agent on my own infrastructure?",
    answer:
      "Yes. The entire Churninator Forge and backend is open-source. Our Enterprise plan includes support for deploying the entire platform, including the fine-tuned inference models, into your own cloud environment for maximum security and control.",
  },
  {
    question:
      "How is this different from a normal analytics tool like Hotjar or FullStory?",
    answer:
      "Analytics tools are fantastic for understanding what users are doing on YOUR OWN site. Churninator is designed to give you that same level of insight for ANY OTHER site on the internet, especially your competitors. It's a competitive intelligence tool, not an internal analytics platform.",
  },
];

export function Faq() {
  return (
    <section id="faq" className="py-16 md:py-32">
      <div className="mx-auto max-w-3xl px-6">
        <div className="text-center">
          <h2 className="text-4xl font-semibold tracking-tight md:text-5xl">
            Frequently Asked Questions
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to know before you unleash the agent.
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
