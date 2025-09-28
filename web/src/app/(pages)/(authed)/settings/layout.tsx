import { SettingsSidebar } from "@/components/dashboard/settings-sidebar";

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="container mx-auto max-w-8xl py-8">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
        <aside className="md:col-span-1">
          <SettingsSidebar />
        </aside>
        <main className="md:col-span-3">{children}</main>
      </div>
    </div>
  );
}
