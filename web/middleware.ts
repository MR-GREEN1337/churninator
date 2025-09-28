// web/middleware.ts
export { default } from "next-auth/middleware";

export const config = {
  // Protect all routes under the following paths
  matcher: [
    "/dashboard/:path*",
    "/settings/:path*",
    "/settings/api/:path*",
    "/history/:path*",
  ],
};
