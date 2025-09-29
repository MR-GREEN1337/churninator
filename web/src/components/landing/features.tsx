import {
  Bot,
  Fingerprint,
  SearchCheck,
  Settings2,
  Sparkles,
  Zap,
} from "lucide-react";

export function Features() {
  return (
    <section id="features" className="py-16 md:py-32">
      <div className="mx-auto max-w-5xl space-y-8 px-6 md:space-y-16">
        <div className="relative z-10 mx-auto max-w-2xl space-y-6 text-center md:space-y-8">
          <h2 className="text-balance text-4xl font-semibold tracking-tight md:text-5xl">
            Go Beyond Analytics. Get Actionable Intelligence.
          </h2>
          <p className="text-lg text-muted-foreground">
            Churninator provides a suite of tools to autonomously analyze web
            applications, identify friction, and deliver insights that human
            testers can miss.
          </p>
        </div>

        {/* --- START: Corrected Grid Classes --- */}
        <div className="relative mx-auto grid max-w-lg divide-y border sm:max-w-2xl sm:grid-cols-2 sm:divide-x sm:divide-y-0 lg:max-w-4xl lg:grid-cols-3 *:p-8">
          {/* --- END: Corrected Grid Classes --- */}
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Zap className="size-5 text-primary" />
              <h3 className="text-lg font-semibold">Autonomous Analysis</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              Deploy an agent in seconds. It navigates complex web apps on its
              own, saving you hours of manual testing and analysis.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Bot className="size-5 text-primary" />
              <h3 className="text-lg font-semibold">Vision-Powered AI</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              Powered by a fine-tuned Vision-Language Model, our agent sees and
              understands UIs just like a human, but with perfect recall.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Fingerprint className="size-5 text-primary" />
              <h3 className="text-lg font-semibold">Data Privacy & Control</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              Run Churninator in your own cloud with our Enterprise plan. Your
              competitive research and reports never leave your infrastructure.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <SearchCheck className="size-5 text-primary" />
              <h3 className="text-lg font-semibold">Targeted Missions</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              Define a specific objective, from analyzing a full signup flow to
              testing a single feature, to get precisely the insights you need.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Settings2 className="size-5 text-primary" />
              <h3 className="text-lg font-semibold">Real-Time Observatory</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              Watch the agent's progress live. See its 'thoughts' and every
              action it takes, giving you complete transparency.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Sparkles className="size-5 text-primary" />
              <h3 className="text-lg font-semibold">AI-Generated Reports</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              Receive detailed friction reports with actionable recommendations
              and AI-generated mockups showing how to improve the UX.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
