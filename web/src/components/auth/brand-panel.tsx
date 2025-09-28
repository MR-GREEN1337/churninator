"use client";

import React, { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";

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
      {/* Animated Aurora Background Blobs (z-0) */}
      <div className="absolute inset-0 z-0">
        <motion.div
          className="absolute top-0 left-0 h-96 w-96 rounded-full bg-primary/30"
          animate={{
            x: [0, 100, 0, -50],
            y: [0, -50, 100, 0],
            scale: [1, 1.2, 1],
            rotate: [0, 0, 180, 0],
          }}
          transition={{
            duration: 30,
            ease: "easeInOut",
            repeat: Infinity,
            repeatType: "mirror",
          }}
          style={{ filter: "blur(100px)" }}
        />
        <motion.div
          className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-blue-500/30"
          animate={{
            x: [0, -100, 0, 50],
            y: [0, 50, -100, 0],
            scale: [1, 1.1, 1],
            rotate: [0, 180, 0, 0],
          }}
          transition={{
            duration: 25,
            ease: "easeInOut",
            repeat: Infinity,
            repeatType: "mirror",
          }}
          style={{ filter: "blur(100px)" }}
        />
      </div>

      {/* Dither/Scanline Overlay (z-1) */}
      <div
        className="
          absolute inset-0 z-[1]
          bg-[image:repeating-linear-gradient(transparent,transparent_2px,theme(colors.black/0.5)_2px,theme(colors.black/0.5)_3px)]
          bg-[size:4px_4px]
          opacity-20
          [mask-image:radial-gradient(ellipse_at_center,black_50%,transparent_100%)]
        "
      />

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
              className="max-w-md text-4xl font-bold leading-tight text-white"
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
