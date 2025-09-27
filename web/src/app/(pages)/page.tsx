// web/src/app/page.tsx
import { HeroSection } from "@/components/landing/hero";
import { Features } from "@/components/landing/features";
import { Pricing } from "@/components/landing/pricing";
import { Faq } from "@/components/landing/faq";
import { Cta } from "@/components/landing/cta";
import Footer from "@/components/landing/footer";

const footerLeftLinks = [
  { href: "#features", label: "Features" },
  { href: "#pricing", label: "Pricing" },
  { href: "#faq", label: "FAQ" },
  { href: "#", label: "Status" },
];

const footerRightLinks = [
  { href: "#", label: "Twitter" },
  { href: "#", label: "GitHub" }, // Changed to GitHub
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
];

// Reusable separator component to connect the inner vertical lines
const SectionSeparator = () => (
  <div className="relative" aria-hidden="true">
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

      {/* This wrapper contains all content below the hero */}
      <div className="relative">
        {/* The decorative vertical lines */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 z-[-1] hidden lg:block [mask-image:linear-gradient(to_bottom,black_0%,black_90%,transparent_100%)]"
        >
          {/* Left pair of lines */}
          <div className="absolute left-[5%] top-0 h-full w-px bg-border" />
          <div className="absolute left-[calc(5%+1.5rem)] top-0 h-full w-px bg-border" />

          {/* Right pair of lines */}
          <div className="absolute right-[5%] top-0 h-full w-px bg-border" />
          <div className="absolute right-[calc(5%+1.5rem)] top-0 h-full w-px bg-border" />
        </div>

        {/* Page sections */}
        <Features />
        <SectionSeparator />
        <Pricing />
        <SectionSeparator />
        <Faq />
        <SectionSeparator />
        <Cta />
        <SectionSeparator />

        <Footer
          leftLinks={footerLeftLinks}
          rightLinks={footerRightLinks}
          copyrightText="Churninator Labs, Inc. All rights reserved."
        />
      </div>
    </div>
  );
}
