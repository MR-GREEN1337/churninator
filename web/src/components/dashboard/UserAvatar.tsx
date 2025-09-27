// web/src/components/dashboard/UserAvatar.tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { User } from "lucide-react"; // Assuming a User type

// In a real app, the user object would have an image property
type UserProps = {
  // A simplified user type for this example
  full_name?: string | null;
  email?: string | null;
  image_url?: string | null;
};

export function UserAvatar({ user }: { user: UserProps | null }) {
  const fallback = user?.full_name?.charAt(0) || user?.email?.charAt(0) || "U";
  return (
    <Avatar className="h-8 w-8">
      <AvatarImage
        src={user?.image_url || undefined}
        alt={user?.full_name || "User"}
      />
      <AvatarFallback>
        <span className="sr-only">{user?.full_name}</span>
        {fallback.toUpperCase()}
      </AvatarFallback>
    </Avatar>
  );
}
