import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    question: "Is my conversation data private and secure?",
    answer:
      "Absolutely. Privacy is at the core of Recast. Your data is encrypted, processed securely, and is never used for training our models. We delete your transcripts after analysis is complete. Your conversations are yours alone.",
  },
  {
    question: "What kind of conversations can I analyze?",
    answer:
      "Recast is designed for a wide range of high-stakes conversations. This includes sales calls, job interviews, team meetings, public speaking practice, and even personal discussions. If it's a conversation you want to improve, you can analyze it with Recast.",
  },
  {
    question: "How does the AI Sparring Ring work?",
    answer:
      "The Sparring Ring uses a custom AI persona that you choose (like a skeptical investor or an angry customer). It engages in a real-time, text-based conversation with you, adapting to your responses to provide a realistic and challenging practice environment. It's a safe space to build muscle memory for difficult conversations.",
  },
  {
    question: "Can I cancel my subscription at any time?",
    answer:
      "Yes. You can cancel your subscription at any time from your billing settings. Your plan will remain active until the end of the current billing period, and you won't be charged again.",
  },
  {
    question: "Do you offer plans for teams or businesses?",
    answer:
      "Yes, we do. Our Teams plan includes everything in Pro, plus features like centralized billing, team performance dashboards, and custom onboarding. Please contact our sales team for custom pricing and a demo.",
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
            Have questions? We have answers. If you can't find what you're
            looking for, feel free to contact us.
          </p>
        </div>
        <div className="mt-12">
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem value={`item-${index}`} key={index}>
                <AccordionTrigger className="text-left">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-base">
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
