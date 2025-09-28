"use client";
import { redirect } from "next/navigation";

// Redirect from the base /settings route to the first page, /settings/profile
export default function SettingsPage() {
  redirect("/settings/profile");
}
