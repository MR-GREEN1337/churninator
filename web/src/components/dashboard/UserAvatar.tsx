// web/src/components/dashboard/UserAvatar.tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

type UserProps = {
  full_name?: string | null;
  email?: string | null;
  image?: string | null;
};

export function UserAvatar({ user }: { user: UserProps | null }) {
  const fallback = user?.full_name?.charAt(0) || user?.email?.charAt(0) || "U";
  return (
    <Avatar className="h-8 w-8">
      <AvatarImage
        src={user?.image || undefined}
        alt={user?.full_name || "User"}
      />
      <AvatarFallback>
        <span className="sr-only">{user?.full_name}</span>
        {fallback.toUpperCase()}
      </AvatarFallback>
    </Avatar>
  );
}
