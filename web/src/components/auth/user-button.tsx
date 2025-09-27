"use client";

//import { useSession } from "next-auth/react";
import { UserDropdown } from "./user-dropdown";
import { Button } from "../ui/button";
import Link from "next/link";
import { Skeleton } from "../ui/skeleton";

export function UserButton() {
  const {
    // @ts-ignore
    data: session,
    // @ts-ignore
    status,
  } = () => {
    return {
      data: {
        user: {
          name: "John Doe",
          email: "john.doe@example.com",
        },
      },
      status: "authenticated",
    };
  };

  // While the session is loading, show a placeholder
  if (status === "loading") {
    return <Skeleton className="h-8 w-8 rounded-full" />;
  }

  // If there's no user session, show login/signup buttons
  if (!session?.user) {
    return (
      <>
        <Button asChild variant="ghost" size="sm">
          <Link href="/login">Login</Link>
        </Button>
        <Button asChild size="sm">
          <Link href="/signup">Sign Up</Link>
        </Button>
      </>
    );
  }

  // If the user is logged in, show the user dropdown
  return <UserDropdown user={session.user} />;
}
