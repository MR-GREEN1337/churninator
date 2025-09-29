"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { FaGithub, FaGoogle } from "react-icons/fa";

// --- START: Accept a prop to control the default state ---
export function AuthForm({
  isSignUpDefault = false,
}: {
  isSignUpDefault?: boolean;
}) {
  const [isSignUp, setIsSignUp] = useState(isSignUpDefault);
  // --- END: Accept a prop to control the default state ---
  const [isLoading, setIsLoading] = useState(false);

  const handleCredentialsSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    setIsLoading(true);
    const formData = new FormData(event.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    if (isSignUp) {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/register`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email,
              password,
              full_name: formData.get("full-name") || email.split("@")[0],
            }),
          },
        );
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Sign up failed.");
        }
        toast.success("Account created! Signing you in...");
        const signInResponse = await signIn("credentials", {
          email,
          password,
          redirect: false,
        });
        if (signInResponse?.ok) {
          window.location.href = "/dashboard";
        } else {
          throw new Error(
            signInResponse?.error || "Sign in after registration failed.",
          );
        }
      } catch (error: any) {
        toast.error("Sign Up Error", { description: error.message });
        setIsLoading(false);
      }
    } else {
      const result = await signIn("credentials", {
        email,
        password,
        redirect: false,
      });
      if (result?.error) {
        toast.error("Login Failed", {
          description: "Incorrect email or password.",
        });
        setIsLoading(false);
      } else if (result?.ok) {
        window.location.href = "/dashboard";
      }
    }
  };

  return (
    <form onSubmit={handleCredentialsSubmit}>
      <div className="grid gap-4">
        {isSignUp && (
          <div className="grid gap-2">
            <Label htmlFor="full-name">Full Name</Label>
            <Input id="full-name" name="full-name" placeholder="John Doe" />
          </div>
        )}
        <div className="grid gap-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="m@example.com"
            required
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" name="password" type="password" required />
        </div>
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isSignUp ? "Create account" : "Sign in"}
        </Button>
        <div className="mt-4 text-center text-sm">
          {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            type="button"
            onClick={() => setIsSignUp(!isSignUp)}
            className="underline"
            disabled={isLoading}
          >
            {isSignUp ? "Sign in" : "Sign up"}
          </button>
        </div>
        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">
              Or continue with
            </span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Button
            variant="outline"
            type="button"
            onClick={() => signIn("github", { callbackUrl: "/dashboard" })}
            disabled={isLoading}
          >
            <FaGithub className="mr-2 h-4 w-4" /> GitHub
          </Button>
          <Button
            variant="outline"
            type="button"
            onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
            disabled={isLoading}
          >
            <FaGoogle className="mr-2 h-4 w-4" /> Google
          </Button>
        </div>
      </div>
    </form>
  );
}
