"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MoreHorizontal,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  BotMessageSquare,
  Settings,
  History,
  Pencil,
  Copy,
  Trash2,
  Sun,
  Moon,
  Globe, // Added Globe icon for fallback
} from "lucide-react";
import { cn, getFaviconUrl, getDomainFromUrl } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import { useTheme } from "next-themes";
import { Logo } from "@/components/shared/logo";

// --- TYPE DEFINITIONS & MOCK DATA ---
type AgentRun = {
  id: string;
  name: string;
  status: "RUNNING" | "COMPLETED" | "FAILED";
  targetUrl: string;
  createdAt: string;
};

const mockAgentRuns: AgentRun[] = [
  {
    id: "run-1",
    name: "Onboard Vercel",
    status: "RUNNING",
    targetUrl: "https://vercel.com",
    createdAt: new Date().toISOString(),
  },
  {
    id: "run-2",
    name: "Test Clerk Signup",
    status: "RUNNING",
    targetUrl: "https://clerk.com",
    createdAt: new Date().toISOString(),
  },
  {
    id: "run-3",
    name: "Analyze Stripe Pricing",
    status: "COMPLETED",
    targetUrl: "https://stripe.com",
    createdAt: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "run-4",
    name: "Scrape GitHub Homepage",
    status: "FAILED",
    targetUrl: "https://github.com",
    createdAt: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: "run-5",
    name: "A very long run name to test...",
    status: "COMPLETED",
    targetUrl: "https://this-is-a-very-long-domain-name-example.co",
    createdAt: new Date(Date.now() - 8 * 86400000).toISOString(),
  },
];

// --- FAVICON COMPONENT WITH FALLBACK ---
function FaviconWithFallback({
  domain,
  size = 24,
  className = "",
}: {
  domain: string;
  size?: number;
  className?: string;
}) {
  const [faviconError, setFaviconError] = useState(false);
  const faviconUrl = getFaviconUrl(domain, size);

  if (faviconError) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-muted rounded-sm",
          className,
        )}
      >
        <Globe
          className={cn(
            "text-muted-foreground",
            size === 32 ? "h-5 w-5" : "h-4 w-4",
          )}
        />
      </div>
    );
  }

  return (
    <img
      src={faviconUrl}
      alt={`Favicon for ${domain}`}
      className={cn("rounded-sm", className)}
      width={size}
      height={size}
      onError={() => setFaviconError(true)}
    />
  );
}

// --- Sub-components for better structure ---
function StatusIndicator({ status }: { status: AgentRun["status"] }) {
  return (
    <div
      className={cn(
        "h-2.5 w-2.5 rounded-full shrink-0",
        status === "RUNNING" && "bg-blue-500 animate-pulse",
        status === "COMPLETED" && "bg-green-500",
        status === "FAILED" && "bg-red-500",
      )}
    />
  );
}

function RunItem({
  run,
  isCollapsed,
}: {
  run: AgentRun;
  isCollapsed: boolean;
}) {
  const pathname = usePathname();
  const href = `/dashboard/run/${run.id}`;
  const isActive = pathname === href;
  const domain = getDomainFromUrl(run.targetUrl);

  // --- COLLAPSED VIEW: FAVICON WITH TIGHTER CORNER STATUS ---
  if (isCollapsed) {
    return (
      <TooltipProvider delayDuration={0}>
        <Tooltip>
          <TooltipTrigger asChild>
            <Link
              href={href}
              className={cn(
                "relative flex h-12 w-12 items-center justify-center rounded-lg transition-transform hover:scale-105",
                isActive && "bg-accent",
              )}
            >
              {/* Active State Ring */}
              <div
                className={cn(
                  "absolute inset-0 rounded-lg ring-2 ring-offset-2 ring-offset-background transition-all",
                  isActive ? "ring-primary" : "ring-transparent",
                )}
              />
              {/* Favicon with Fallback */}
              <FaviconWithFallback
                domain={domain}
                size={32}
                className="h-8 w-8"
              />
              {/* TIGHTER CORNER STATUS INDICATOR */}
              <div className="absolute -bottom-0.5 -right-0.5">
                <StatusIndicator status={run.status} />
              </div>
            </Link>
          </TooltipTrigger>
          <TooltipContent side="right">
            <p className="font-semibold">{run.name}</p>
            <p className="text-xs text-muted-foreground">{run.targetUrl}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  // --- EXPANDED VIEW: NOW WITH FAVICON AND TEXT ---
  return (
    <Link
      href={href}
      className={cn(
        "group flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent",
        isActive
          ? "bg-accent text-accent-foreground"
          : "text-muted-foreground hover:text-accent-foreground",
      )}
    >
      <div className="flex items-center gap-3 min-w-0">
        {/* Favicon in Expanded View */}
        <div className="relative shrink-0">
          <FaviconWithFallback domain={domain} size={24} className="h-6 w-6" />
          <div className="absolute -bottom-0.5 -right-0.5">
            <StatusIndicator status={run.status} />
          </div>
        </div>
        <span className="truncate">{run.name}</span>
      </div>
      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
              }}
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-40">
            <DropdownMenuItem onClick={() => alert(`Rename ${run.id}`)}>
              <Pencil className="mr-2 h-4 w-4" /> <span>Rename</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => alert(`Duplicate ${run.id}`)}>
              <Copy className="mr-2 h-4 w-4" /> <span>Duplicate</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={() => alert(`Delete ${run.id}`)}
            >
              <Trash2 className="mr-2 h-4 w-4" /> <span>Delete</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </Link>
  );
}

function ThemeToggle({ isCollapsed }: { isCollapsed: boolean }) {
  const { setTheme } = useTheme();
  return (
    <TooltipProvider delayDuration={0}>
      <Tooltip>
        <TooltipTrigger asChild>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className={cn(
                  "w-full",
                  isCollapsed
                    ? "justify-center"
                    : "justify-start gap-3 rounded-md px-3 py-2",
                )}
              >
                <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                {!isCollapsed && <span>Theme</span>}
                <span className="sr-only">Toggle theme</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="start"
              side={isCollapsed ? "right" : "top"}
            >
              <DropdownMenuItem onClick={() => setTheme("light")}>
                Light
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("dark")}>
                Dark
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("system")}>
                System
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </TooltipTrigger>
        <TooltipContent side="right">Toggle Theme</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

// --- MAIN SIDEBAR COMPONENT ---
export function Sidebar({
  isCollapsed,
  setIsCollapsed,
}: {
  isCollapsed: boolean;
  setIsCollapsed: (isCollapsed: boolean) => void;
}) {
  const agentRuns = mockAgentRuns;

  const runGroups = useMemo(() => {
    const groups: { [key: string]: AgentRun[] } = { Running: [], Recent: [] };
    const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    agentRuns.forEach((run) => {
      if (run.status === "RUNNING") groups["Running"].push(run);
      else if (new Date(run.createdAt) > sevenDaysAgo)
        groups["Recent"].push(run);
    });
    return groups;
  }, [agentRuns]);

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col border-r bg-background transition-all duration-300 ease-in-out",
        isCollapsed ? "w-20" : "w-72",
      )}
    >
      {/* Header */}
      <div
        className={cn(
          "flex h-16 shrink-0 items-center border-b",
          isCollapsed ? "justify-center" : "px-4",
        )}
      >
        <Logo hideText={isCollapsed} />
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col gap-4 py-4">
        <div className="px-4">
          <TooltipProvider delayDuration={0}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  asChild
                  className="w-full"
                  size={isCollapsed ? "icon" : "default"}
                >
                  <Link href="/dashboard">
                    <Plus className="h-4 w-4" />
                    {!isCollapsed && (
                      <span className="ml-2">New Agent Run</span>
                    )}
                  </Link>
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">New Agent Run</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>

        <ScrollArea className="flex-1 px-2">
          <nav className="grid gap-1 px-2">
            {Object.entries(runGroups).map(
              ([groupName, groupRuns]) =>
                groupRuns.length > 0 && (
                  <div key={groupName} className="py-2">
                    <h3
                      className={cn(
                        "text-xs font-semibold text-muted-foreground px-3 mb-2 tracking-wider",
                        isCollapsed && "text-center",
                      )}
                    >
                      {isCollapsed
                        ? groupName.substring(0, 3).toUpperCase()
                        : groupName}
                    </h3>
                    <div
                      className={cn(
                        "space-y-1",
                        isCollapsed &&
                          "grid grid-cols-1 justify-items-center gap-2",
                      )}
                    >
                      {groupRuns.map((run) => (
                        <RunItem
                          key={run.id}
                          run={run}
                          isCollapsed={isCollapsed}
                        />
                      ))}
                    </div>
                  </div>
                ),
            )}
          </nav>
        </ScrollArea>
      </div>

      {/* Footer */}
      <div className="mt-auto border-t p-2 space-y-1">
        <TooltipProvider delayDuration={0}>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                asChild
                variant="ghost"
                className={cn(
                  "w-full",
                  isCollapsed ? "justify-center" : "justify-start",
                )}
              >
                <Link href="/history">
                  <History className="h-4 w-4" />
                  {!isCollapsed && <span className="ml-3">Full History</span>}
                </Link>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">Full History</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                asChild
                variant="ghost"
                className={cn(
                  "w-full",
                  isCollapsed ? "justify-center" : "justify-start",
                )}
              >
                <Link href="/settings">
                  <Settings className="h-4 w-4" />
                  {!isCollapsed && <span className="ml-3">Settings</span>}
                </Link>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">Settings</TooltipContent>
          </Tooltip>
          <ThemeToggle isCollapsed={isCollapsed} />
        </TooltipProvider>
      </div>

      {/* Collapse Button */}
      <div className="border-t p-2">
        <TooltipProvider delayDuration={0}>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                onClick={() => setIsCollapsed(!isCollapsed)}
                variant="ghost"
                className="w-full justify-start gap-3"
              >
                {isCollapsed ? (
                  <PanelLeftOpen className="h-5 w-5 mx-auto" />
                ) : (
                  <PanelLeftClose className="h-5 w-5" />
                )}
                {!isCollapsed && <span>Collapse</span>}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              {isCollapsed ? "Expand" : "Collapse"}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </aside>
  );
}
