import { AuthForm } from "@/components/auth/auth-form";

export default function SignupPage() {
  return (
    <div className="mx-auto grid w-[350px] gap-6">
      <div className="grid gap-2 text-center">
        <h1 className="text-3xl font-bold">Create an Account</h1>
        <p className="text-balance text-muted-foreground">
          Enter your details below to start your first mission.
        </p>
      </div>
      {/* Pass the prop to set the form's initial state to "Sign Up" */}
      <AuthForm isSignUpDefault={true} />
    </div>
  );
}
