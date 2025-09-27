// web/src/components/shared/logo.tsx

"use client";

import React from "react";
import Link from "next/link";
import { Playfair_Display } from "next/font/google";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";

const playfair = Playfair_Display({
  subsets: ["latin"],
  weight: "700",
});

interface LogoProps {
  className?: string;
  hideText?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ className, hideText = true }) => {
  const pathname = usePathname();

  return (
    <Link
      href={
        pathname.startsWith("/dashboard") ||
        pathname.startsWith("/sparring") ||
        pathname.startsWith("/replay") ||
        pathname.startsWith("/settings")
          ? "/dashboard"
          : "/"
      }
      className={cn(
        "group flex items-center gap-2.5 transition-opacity duration-300 hover:opacity-80",
        className,
      )}
      aria-label="Recast Homepage"
    >
      <div className="h-7 w-7">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
          className="h-full w-full transition-transform duration-500 ease-in-out"
        >
          {/* The two arcs form the "Dialogue Mark" */}
          <path
            d="M8 5C4.68629 5 2 7.68629 2 11"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            className="origin-center transition-transform duration-300 ease-in-out group-hover:rotate-[-6deg]"
          />
          <path
            d="M16 19C19.3137 19 22 16.3137 22 13"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            className="origin-center transition-transform duration-300 ease-in-out group-hover:rotate-[-6deg]"
          />
        </svg>
      </div>
      {!hideText && (
        <span
          className={cn(
            "text-xl font-bold tracking-tighter text-foreground",
            playfair.className,
            className,
          )}
        >
          Recast
        </span>
      )}
    </Link>
  );
};

export default Logo;
