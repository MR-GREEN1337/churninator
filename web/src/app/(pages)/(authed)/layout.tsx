"use client";

import { useState } from "react";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Header } from "@/components/dashboard/header"; // <-- IMPORT THE NEW HEADER

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-muted/40">
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
      />

      <div className="flex flex-1 flex-col overflow-y-auto">
        <Header /> {/* <-- USE THE NEW HEADER HERE */}
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
