import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

export default withAuth(
  // The `withAuth` middleware augments your `Request` with the user's token.
  // We don't need any custom logic here, so we just return the default response.
  function middleware(req) {
    return NextResponse.next();
  },
  {
    callbacks: {
      // The `authorized` callback is the heart of the security.
      // It returns `true` if the user has a token (is logged in), allowing access.
      // Otherwise, it returns `false`, triggering the redirect.
      authorized: ({ token }) => !!token,
    },
    pages: {
      // If `authorized` returns `false`, the user is redirected to this page.
      signIn: "/login",
    },
  },
);

// This is the crucial part that defines which routes are protected.
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones that are explicitly public.
     * This is a "default-deny" approach, which is more secure.
     *
     * - The root landing page (`/`) is public.
     * - Auth pages (`/login`, `/signup`) are public.
     * - Next.js internal paths (`/_next/...`, `/api/...`, etc.) are ignored.
     *
     * Any other path, like `/dashboard`, `/settings`, `/history`, etc.,
     * will be matched and therefore protected by the middleware.
     */
    "/((?!api|_next/static|_next/image|favicon.ico|login|signup|^/$).*)",
  ],
};
