// Remove 'use client' if it's there
import { getServerSession } from "next-auth"; // <-- Import getServerSession
import { authOptions } from "@/app/api/auth/[...nextauth]/route"; // <-- Import authOptions
import { UserDropdown } from "./user-dropdown";
import { Button } from "../ui/button";
import Link from "next/link";
import { Skeleton } from "../ui/skeleton";

// Make the component async
export async function UserButton() {
  // Fetch session on the server
  const session = await getServerSession(authOptions);

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
  const userProps = {
    name: session.user.name ?? "",
    email: session.user.email ?? "",
    image: session.user.image ?? "",
  };

  return <UserDropdown user={userProps} />;
}
