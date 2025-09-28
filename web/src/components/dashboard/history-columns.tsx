"use client";

import { ColumnDef } from "@tanstack/react-table";
import { AgentRun } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Eye, MoreHorizontal } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";
import { getDomainFromUrl } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";

export const columns: ColumnDef<AgentRun>[] = [
  {
    accessorKey: "target_url",
    header: "Target",
    cell: ({ row }) => {
      const domain = getDomainFromUrl(row.original.target_url);
      return <div className="font-medium">{domain}</div>;
    },
  },
  {
    accessorKey: "task_prompt",
    header: "Objective",
    cell: ({ row }) => {
      const prompt = row.getValue("task_prompt") as string;
      const truncatedPrompt =
        prompt.length > 50 ? prompt.substring(0, 50) + "..." : prompt;
      return <div className="text-muted-foreground">{truncatedPrompt}</div>;
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as AgentRun["status"];
      const variant =
        {
          COMPLETED: "default",
          RUNNING: "secondary",
          PENDING: "outline",
          FAILED: "destructive",
        }[status] || "default";

      return (
        <Badge variant={variant as any} className="capitalize">
          {status.toLowerCase()}
        </Badge>
      );
    },
  },
  {
    accessorKey: "created_at",
    header: "Date",
    cell: ({ row }) => {
      const date = new Date(row.getValue("created_at"));
      return (
        <div className="text-muted-foreground">
          {formatDistanceToNow(date, { addSuffix: true })}
        </div>
      );
    },
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const run = row.original;
      return (
        <div className="text-right">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuItem asChild>
                <Link href={`/dashboard/run/${run.id}`}>
                  <Eye className="mr-2 h-4 w-4" /> View Details
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-destructive"
                onClick={() => alert(`Delete run ${run.id}`)}
              >
                Delete Run
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      );
    },
  },
];
