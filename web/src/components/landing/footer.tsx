"use client";
import React, { useEffect, useRef, useState } from "react";
import { useTheme } from "next-themes";
import { Logo } from "../shared/logo";

interface LinkItem {
  href: string;
  label: string;
}

interface FooterProps {
  leftLinks: LinkItem[];
  rightLinks: LinkItem[];
  copyrightText: string;
  barCount?: number; // This prop is unused, can be removed if not needed for other animations
}

const Footer: React.FC<FooterProps> = ({
  leftLinks,
  rightLinks,
  copyrightText,
}) => {
  // --- START TEXT UPDATE: Align footer text with Churninator's mission ---
  const missionStatement =
    "Our mission is to give product teams an unfair advantage by providing autonomous, AI-driven insights into their competitors' user experience.";
  // --- END TEXT UPDATE ---

  const handleBackToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer className="relative w-full select-none pb-12 pt-16 mb-40 pb-10">
      <div className="container mx-auto flex flex-col gap-12 px-6 md:flex-row md:justify-between">
        {/* --- LEFT COLUMN: BRAND --- */}
        <div className="space-y-4">
          <Logo hideText={false} />
          <p className="max-w-xs text-sm text-muted-foreground">
            {missionStatement}
          </p>
        </div>

        {/* --- RIGHT COLUMN: NAV & UTILITY --- */}
        <div className="space-y-8 text-left md:text-right">
          <ul className="flex flex-wrap justify-start gap-x-6 gap-y-2 md:justify-end">
            {[...leftLinks, ...rightLinks].map((link, index) => (
              <li key={index}>
                <a
                  href={link.href}
                  target={link.href.startsWith("http") ? "_blank" : undefined}
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
          <div className="flex flex-col items-start md:items-end gap-4">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} {copyrightText}
            </p>
            <button
              onClick={handleBackToTop}
              className="inline-flex items-center text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              Back to top ↑
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
