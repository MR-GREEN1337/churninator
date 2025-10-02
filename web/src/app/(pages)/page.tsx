// web/src/app/page.tsx
import { HeroSection } from "@/components/landing/hero";
import { Features } from "@/components/landing/features";
import { Pricing } from "@/components/landing/pricing";
import { Faq } from "@/components/landing/faq";
import { CTASection } from "@/components/landing/cta";
import Footer from "@/components/landing/footer";
import { Testimonials } from "@/components/landing/testimonials";
import { OpenSourceSection } from "@/components/landing/open-source-section";

// This static data can remain here
const footerLeftLinks = [
  { href: "#features", label: "Features" },
  { href: "#pricing", label: "Pricing" },
  { href: "#faq", label: "FAQ" },
  { href: "#", label: "Status" },
];

const footerRightLinks = [
  { href: "#", label: "Twitter" },
  { href: "https://github.com/MR-GREEN1337/churninator", label: "GitHub" },
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
];

const SectionSeparator = () => (
  <div className="relative z-10" aria-hidden="true">
    <div className="absolute inset-0 flex items-center">
      <div
        className="w-full border-t border-border"
        style={{
          marginLeft: "calc(5% + 1.5rem)",
          marginRight: "calc(5% + 1.5rem)",
        }}
      />
    </div>
  </div>
);

export default function Home() {
  return (
    <div className="flex flex-col">
      <HeroSection />

      {/* This wrapper contains all content below the hero, INCLUDING THE FOOTER */}
      <div className="relative">
        {/* The decorative vertical lines */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 z-10 hidden lg:block [mask-image:linear-gradient(to_bottom,black_0%,black_90%,transparent_100%)]"
        >
          <div className="absolute left-[5%] top-0 h-full w-px bg-border" />
          <div className="absolute left-[calc(5%+1.5rem)] top-0 h-full w-px bg-border" />
          <div className="absolute right-[5%] top-0 h-full w-px bg-border" />
          <div className="absolute right-[calc(5%+1.5rem)] top-0 h-full w-px bg-border" />
        </div>

        {/* Page sections */}
        <Features />
        <SectionSeparator />
        <OpenSourceSection />
        <SectionSeparator />
        <Testimonials />
        <SectionSeparator />
        <Pricing />
        <SectionSeparator />
        <Faq />
        <SectionSeparator />
        <CTASection />
        <SectionSeparator />

        {/* --- FIX: THE FOOTER IS NOW MOVED INSIDE THIS CONTAINER --- */}
        <Footer />
        {/* --- END FIX --- */}
      </div>
    </div>
  );
}
