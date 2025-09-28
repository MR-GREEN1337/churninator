"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Search,
  PanelLeft,
  PlusCircle,
  LogOut,
  Settings,
  LifeBuoy,
  History,
  Wallet,
  Home,
} from "lucide-react";
import { useSession, signOut } from "next-auth/react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuGroup,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Logo } from "@/components/shared/logo";
import { CommandPalette } from "./CommandPalette";
import { UserAvatar } from "./UserAvatar";
import { DynamicBreadcrumb } from "../shared/Breadcrumbs";
import { cn } from "@/lib/utils";

const mobileNavItems = [
  { href: "/dashboard", icon: Home, label: "Dashboard" },
  { href: "/history", icon: History, label: "Run History" },
  { href: "/settings", icon: Settings, label: "Settings" },
  { href: "/support", icon: LifeBuoy, label: "Support" },
];

export function Header({ className }: { className?: string }) {
  const { data: session } = useSession();
  const user = session?.user;
  const [isCommandOpen, setCommandOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCommandOpen((open) => !open);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const displayName = useMemo(
    () => user?.name || user?.email?.split("@")[0] || "User",
    [user],
  );

  const userAvatarProps = {
    full_name: user?.name,
    email: user?.email,
    image: user?.image,
  };

  return (
    <>
      <header
        className={cn(
          "sticky top-0 z-30 flex h-12 items-center justify-between gap-4 border-b bg-background px-4 sm:px-6",
          className,
        )}
      >
        <div className="flex items-center gap-4">
          <Sheet>
            <SheetTrigger asChild>
              <Button size="icon" variant="outline" className="sm:hidden">
                <PanelLeft className="h-5 w-5" />
                <span className="sr-only">Toggle Menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="sm:max-w-xs">
              <nav className="grid gap-6 text-lg font-medium mt-6">
                <Logo />
                {mobileNavItems.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`flex items-center gap-4 px-2.5 ${
                        isActive ? "text-foreground" : "text-muted-foreground"
                      } hover:text-foreground`}
                    >
                      <item.icon className="h-5 w-5" />
                      {item.label}
                    </Link>
                  );
                })}
              </nav>
            </SheetContent>
          </Sheet>
          <DynamicBreadcrumb />
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => setCommandOpen(true)}
          >
            <Search className="h-4 w-4" />
            <span className="sr-only">Search / Command</span>
          </Button>

          <Button asChild size="sm" className="h-8 gap-1">
            <Link href="/dashboard">
              <PlusCircle className="h-4 w-4" />
              <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                New Run
              </span>
            </Link>
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                <UserAvatar user={userAvatarProps} />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none capitalize">
                    {displayName}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {user?.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuGroup>
                <DropdownMenuItem asChild>
                  <Link href="/settings">
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings/billing">
                    <Wallet className="mr-2 h-4 w-4" />
                    Billing
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/support">
                    <LifeBuoy className="mr-2 h-4 w-4" />
                    Support
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuGroup>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => signOut({ callbackUrl: "/" })}
                className="cursor-pointer"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
      <CommandPalette open={isCommandOpen} onOpenChange={setCommandOpen} />
    </>
  );
}
