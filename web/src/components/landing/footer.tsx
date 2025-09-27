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
  barCount?: number;
}

const Footer: React.FC<FooterProps> = ({
  leftLinks,
  rightLinks,
  copyrightText,
  barCount = 50,
}) => {
  const { resolvedTheme } = useTheme();
  const waveRefs = useRef<(HTMLDivElement | null)[]>([]);
  const footerRef = useRef<HTMLDivElement | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const animationFrameRef = useRef<number | null>(null);
  const [waveColor, setWaveColor] = useState("hsl(var(--primary))");

  useEffect(() => {
    setWaveColor(
      resolvedTheme === "light"
        ? "hsl(var(--foreground))"
        : "hsl(var(--primary))",
    );
  }, [resolvedTheme]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 },
    );

    if (footerRef.current) {
      observer.observe(footerRef.current);
    }

    return () => {
      if (footerRef.current) {
        // eslint-disable-next-line react-hooks/exhaustive-deps
        observer.unobserve(footerRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    let t = 0;
    const animateWave = () => {
      waveRefs.current.forEach((element, index) => {
        if (element) {
          const sinValue = Math.sin(t + index * 0.2);
          const offset = (sinValue + 1) * 30;
          element.style.transform = `translateY(${offset}px)`;
        }
      });

      t += 0.05;
      animationFrameRef.current = requestAnimationFrame(animateWave);
    };

    animateWave();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isVisible]);

  const handleBackToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer ref={footerRef} className="relative w-full select-none mb-32 pb-12">
      <div className="container mx-auto flex flex-col gap-12 px-6 pb-24 pt-16 md:flex-row md:justify-between">
        {/* --- LEFT COLUMN: BRAND --- */}
        <div className="space-y-4">
          <Logo hideText={false} />
          <p className="max-w-xs text-sm text-muted-foreground">
            Our mission is to help you master the conversations that matter most
            through private, AI-powered practice and analysis.
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
