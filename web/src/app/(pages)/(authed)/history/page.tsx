// web/src/app/(pages)/(authed)/history/page.tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { columns } from "@/components/dashboard/history-columns";
import { DataTable } from "@/components/dashboard/data-table";
import { api } from "@/lib/api";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { ApiError } from "next/dist/server/api-utils";

async function getHistoryData() {
  // --- START FIX ---
  // 1. Get the session on the server
  const session = await getServerSession(authOptions);

  // 2. Extract the access token
  const accessToken = session?.accessToken;
  // --- END FIX ---

  try {
    // 3. Pass the token to the API call
    const runs = await api.getAgentRuns(accessToken);
    return runs;
  } catch (error: any) {
    if (error instanceof ApiError && (error as any).status === 401) {
      console.error(
        "Authentication error on server-side fetch for history page.",
      );
    } else {
      console.error("Failed to fetch agent runs:", error);
    }
    return []; // Return an empty array on any error
  }
}

export default async function HistoryPage() {
  const data = await getHistoryData();

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <Card>
        <CardHeader>
          <CardTitle>Run History</CardTitle>
          <CardDescription>
            A complete log of all your agent reconnaissance missions.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={data} />
        </CardContent>
      </Card>
    </div>
  );
}
