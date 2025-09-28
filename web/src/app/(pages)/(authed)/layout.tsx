"use client";

import { useState } from "react";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Header } from "@/components/dashboard/header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true);

  return (
    // --- START FIX: Convert layout from Flexbox to CSS Grid ---
    <div className="grid h-screen w-full grid-cols-[auto_1fr] grid-rows-[auto_1fr]">
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
        // Place the sidebar in the first column, spanning both rows
        className="col-start-1 row-start-1 row-span-2"
      />

      <Header
        // Place the header in the second column, first row
        className="col-start-2 row-start-1"
      />

      <main className="col-start-2 row-start-2 overflow-y-auto">
        {children}
      </main>
    </div>
    // --- END FIX ---
  );
}
