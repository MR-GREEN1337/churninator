"use client";

import React, { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Ripple } from "@/components/ui/ripple";

export const BrandPanel = () => {
  // Taglines specifically for The Churninator
  const taglines = [
    "Find your competitor's fatal flaw.",
    "Turn user friction into your advantage.",
    "Where market research becomes autonomous.",
    "Deploy an AI agent. Uncover the truth.",
  ];

  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % taglines.length);
    }, 5000); // Cycle every 5 seconds
    return () => clearInterval(timer);
  }, [taglines.length]);

  return (
    <div className="relative hidden w-1/2 flex-col justify-end overflow-hidden bg-slate-900 p-12 lg:flex">
      {/* --- START FIX: Simplified Background --- */}
      {/* The Ripple component is now the primary background effect */}
      <div className="absolute inset-0 z-0 flex items-center justify-center">
        <Ripple />
      </div>
      {/* --- END FIX --- */}

      {/* Text content, layered on top with a higher z-index (z-10) */}
      <div className="relative z-10">
        {/* Fixed height container to prevent layout shifts */}
        <div className="h-24">
          <AnimatePresence mode="wait">
            <motion.h1
              key={taglines[index]}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
              className="max-w-md text-4xl font-light leading-tight text-white"
            >
              {taglines[index]}
            </motion.h1>
          </AnimatePresence>
        </div>
        <p className="mt-4 max-w-md text-slate-400">
          The autonomous AI mystery shopper for SaaS.
        </p>
      </div>
    </div>
  );
};
