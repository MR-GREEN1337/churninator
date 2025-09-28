// web/src/app/(pages)/(auth)/login/page.tsx
import { AuthForm } from "@/components/auth/auth-form";

export default function LoginPage() {
  return (
    <div className="lg:grid lg:min-h-screen lg:grid-cols-2 xl:min-h-screen">
      <div className="flex items-center justify-center py-12">
        <div className="mx-auto grid w-[350px] gap-6">
          <div className="grid gap-2 text-center">
            <h1 className="text-3xl font-bold">Welcome</h1>
            <p className="text-balance text-muted-foreground">
              Sign in or create an account to continue
            </p>
          </div>
          <AuthForm />
        </div>
      </div>
      <div className="hidden bg-muted lg:block">
        {/* Placeholder for animation - a simple gradient for now */}
        <div className="h-full w-full bg-gradient-to-br from-primary/10 via-transparent to-transparent" />
      </div>
    </div>
  );
}
