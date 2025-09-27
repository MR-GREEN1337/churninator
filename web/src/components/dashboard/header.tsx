// web/src/components/dashboard/header.tsx
import Link from "next/link";
import { PanelLeft, BotMessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
// import { UserButton } from "@/components/auth/user-button";
// import { ThemeToggle } from "@/components/theme-toggle";

interface HeaderProps {
  setSidebarOpen: (open: boolean) => void;
}

export function Header({ setSidebarOpen }: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6 py-4">
      {/* Mobile Sidebar Toggle */}
      <Button
        size="icon"
        variant="outline"
        className="sm:hidden"
        onClick={() => setSidebarOpen(true)}
      >
        <PanelLeft className="h-5 w-5" />
        <span className="sr-only">Toggle Menu</span>
      </Button>

      <div className="flex items-center gap-2">
        <BotMessageSquare className="h-6 w-6 text-primary" />
        <h1 className="text-xl font-semibold">Agent Command</h1>
      </div>

      <div className="ml-auto flex items-center gap-2">
        {/* Placeholder for User Button and Theme Toggle */}
        {/* <ThemeToggle /> */}
        {/* <UserButton /> */}
      </div>
    </header>
  );
}
