"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Menu, X, ArrowUpRight } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Logo } from "../shared/logo";

interface HeaderClientProps {
  menuItems: { name: string; href: string; id: string; withArrow?: boolean }[];
  children: React.ReactNode;
}

export function HeaderClient({ menuItems, children }: HeaderClientProps) {
  const [menuState, setMenuState] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState(menuItems[0].id);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { rootMargin: `-50% 0px -50% 0px` }, // Activates when section is in vertical center
    );

    const sections = menuItems
      .map((item) => document.getElementById(item.id))
      .filter(Boolean);
    sections.forEach((section) => section && observer.observe(section));

    return () =>
      sections.forEach((section) => section && observer.unobserve(section));
  }, [menuItems]);

  return (
    <nav
      data-state={menuState ? "active" : "inactive"}
      className="fixed z-20 w-full px-2 group"
    >
      <div
        className={cn(
          "mx-auto mt-2 flex items-center justify-between transition-all duration-300",
          isScrolled
            ? "max-w-4xl rounded-full border bg-background/80 p-2 pl-4 backdrop-blur-lg shadow-md"
            : "max-w-6xl p-2.5",
        )}
      >
        <div className="flex items-center">
          <Logo hideText={false} />
        </div>

        {/* --- CENTER (Desktop Only): Animated Nav Links --- */}
        <div className="hidden lg:flex">
          <ul
            className={cn(
              "relative flex items-center gap-4 text-sm transition-all duration-300",
              isScrolled && "ml-4",
            )}
          >
            {menuItems.map((item) => (
              <li key={item.id} className="relative">
                <Link
                  href={item.href}
                  onClick={() => setActiveSection(item.id)}
                  className={cn(
                    "block px-3 py-1.5 transition-colors",
                    activeSection === item.id
                      ? "text-foreground"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  <span className="flex items-center">
                    {item.name}
                    {item.withArrow && (
                      <ArrowUpRight className="ml-1 h-3 w-3" />
                    )}
                  </span>
                </Link>
                {activeSection === item.id && (
                  <motion.div
                    layoutId="active-pill"
                    className="absolute inset-0 z-[-1] rounded-full bg-accent"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
              </li>
            ))}
          </ul>
        </div>

        {/* --- RIGHT SIDE: Buttons and Mobile Menu Container --- */}
        <div className="flex items-center gap-2">
          <div className="hidden lg:flex items-center gap-2">{children}</div>

          <button
            onClick={() => setMenuState(!menuState)}
            aria-label={menuState ? "Close Menu" : "Open Menu"}
            className="relative z-20 -m-2.5 block cursor-pointer p-2.5 lg:hidden"
          >
            <Menu className="group-data-[state=inactive]:scale-100 group-data-[state=inactive]:opacity-100 group-data-[state=active]:scale-0 group-data-[state=active]:opacity-0 m-auto size-6 transition-all duration-200" />
            <X className="group-data-[state=inactive]:scale-0 group-data-[state=inactive]:opacity-0 group-data-[state=active]:scale-100 group-data-[state=active]:opacity-100 absolute inset-0 m-auto size-6 transition-all duration-200" />
          </button>
        </div>
      </div>

      {/* --- Mobile Menu Panel --- */}
      <div
        className={cn(
          "lg:hidden",
          "origin-top transition-all duration-300 ease-in-out",
          menuState
            ? "visible scale-100 opacity-100"
            : "invisible scale-95 opacity-0",
        )}
      >
        <div className="absolute left-0 w-full mt-2 rounded-2xl border bg-background/95 p-6 backdrop-blur-lg shadow-xl">
          <ul className="space-y-6 text-base">
            {menuItems.map((item) => (
              <li key={item.id}>
                <Link
                  href={item.href}
                  onClick={() => setMenuState(false)} // Close menu on click
                  className="text-muted-foreground hover:text-foreground block duration-15-0"
                >
                  <span className="flex items-center">
                    {item.name}
                    {item.withArrow && (
                      <ArrowUpRight className="ml-1.5 h-4 w-4" />
                    )}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
          <div className="w-full border-t pt-4 mt-6 flex items-center justify-end gap-2">
            {children}
          </div>
        </div>
      </div>
    </nav>
  );
}
