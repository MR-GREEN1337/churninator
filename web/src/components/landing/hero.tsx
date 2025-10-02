// web/src/components/landing/hero.tsx
import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { HeaderClient } from "./header-client";
import { UserButton } from "../auth/user-button";
import { ThemeToggle } from "../theme-toggle";
import { HeroClientContent } from "./hero-client-content"; // <-- Import our new client component

// menuItems can stay here as it's static data
const menuItems = [
  { name: "Home", href: "#home", id: "home" },
  { name: "Features", href: "#features", id: "features" },
  { name: "Pricing", href: "#pricing", id: "pricing" },
  {
    name: "GitHub",
    href: "https://github.com/MR-GREEN1337/churninator",
    id: "github",
    withArrow: true,
  },
];

// HeroHeader is async, so it must be called from a Server Component
async function HeroHeader() {
  return (
    <header>
      {/* The `UserButton` will now correctly use getServerSession indirectly */}
      <HeaderClient menuItems={menuItems}>
        <Button asChild variant="outline" size="sm">
          <Link href="#">Join Discord</Link>
        </Button>
        <UserButton />
        <ThemeToggle isCollapsed />
      </HeaderClient>
    </header>
  );
}

// The main export is now a clean Server Component
export function HeroSection() {
  return (
    <>
      <HeroHeader />
      <HeroClientContent />
    </>
  );
}
