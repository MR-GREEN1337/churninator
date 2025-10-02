"use client";

import { FlickeringGrid } from "@/components/landing/flickering-grid";
import { useMediaQuery } from "@/hooks/use-media-query";
import { siteConfig } from "@/lib/config";
import { ChevronRightIcon } from "@radix-ui/react-icons";
import Link from "next/link";
import Image from "next/image";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export default function Footer() {
  const tablet = useMediaQuery("(max-width: 1024px)");
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const logoSrc = !mounted
    ? "/churninator-logo.svg"
    : resolvedTheme === "dark"
      ? "/churninator-logo-white.svg"
      : "/churninator-logo.svg";

  return (
    // The main footer container
    <footer id="footer" className="w-full pb-0">
      {/* This container will constrain all content within the page's max-width */}
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between p-10">
          <div className="flex flex-col items-start justify-start gap-y-5 max-w-xs mx-0">
            <Link href="/" className="flex items-center gap-2">
              <Image
                src={logoSrc}
                alt="Churninator Logo"
                width={220}
                height={22}
                priority
              />
            </Link>
            <p className="tracking-tight text-muted-foreground font-medium">
              {siteConfig.hero.description}
            </p>

            {/* --- START FIX: ADDED X AND LINKEDIN ICONS --- */}
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/MR-GREEN1337/churninator"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  className="size-5 text-muted-foreground hover:text-primary transition-colors"
                >
                  <path
                    fill="currentColor"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z"
                  />
                </svg>
              </a>
              <a
                href="#"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="X (formerly Twitter)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  className="size-5 text-muted-foreground hover:text-primary transition-colors"
                >
                  <path
                    fill="currentColor"
                    d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 7.184L18.901 1.153zm-1.653 19.57h2.61L7.131 2.542H4.288z"
                  />
                </svg>
              </a>
              <a
                href="#"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="LinkedIn"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  className="size-5 text-muted-foreground hover:text-primary transition-colors"
                >
                  <path
                    fill="currentColor"
                    d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"
                  />
                </svg>
              </a>
            </div>
            {/* --- END FIX --- */}
          </div>
          <div className="pt-5 md:w-1/2">
            <div className="flex flex-col items-start justify-start md:flex-row md:items-center md:justify-between gap-y-5 lg:pl-10">
              {siteConfig.footerLinks.map((column, columnIndex) => (
                <ul key={columnIndex} className="flex flex-col gap-y-2">
                  <li className="mb-2 text-sm font-semibold text-primary">
                    {column.title}
                  </li>
                  {column.links.map((link) => (
                    <li
                      key={link.id}
                      className="group inline-flex cursor-pointer items-center justify-start gap-1 text-[15px]/snug text-muted-foreground"
                    >
                      <Link href={link.url}>{link.title}</Link>
                      <div className="flex size-4 items-center justify-center border border-border rounded translate-x-0 transform opacity-0 transition-all duration-300 ease-out group-hover:translate-x-1 group-hover:opacity-100">
                        <ChevronRightIcon className="h-4 w-4 " />
                      </div>
                    </li>
                  ))}
                </ul>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* This container enforces the content boundaries defined by the vertical lines */}
      <div
        style={{
          paddingLeft: "calc(5% + 1.5rem)",
          paddingRight: "calc(5% + 1.5rem)",
        }}
      >
        <Link
          href="https://github.com/MR-GREEN1337/churninator"
          target="_blank"
          rel="noopener noreferrer"
          className="block h-48 md:h-64 relative mt-12 z-0 cursor-pointer"
        >
          <div className="absolute inset-0 bg-gradient-to-t from-transparent to-background z-10 from-40%" />
          <div className="absolute inset-0 ">
            <FlickeringGrid
              text={tablet ? "Open Source" : "Open Source - Open Source"}
              fontSize={tablet ? 50 : 80}
              className="h-full w-full"
              squareSize={2}
              gridGap={tablet ? 2 : 3}
              maxOpacity={0.15}
              flickerChance={0.05}
            />
          </div>
        </Link>
      </div>
    </footer>
  );
}
