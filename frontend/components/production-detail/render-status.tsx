"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { StatusIndicator } from "@/components/ui/status-indicator";
import type { StateVariant } from "@/lib/design-system/tokens";

interface RenderJobSummary {
  id: string;
  status: string;
  provider: string;
  created_at: string;
  updated_at: string;
  error_message: string | null;
}

interface RenderStatusProps {
  job: RenderJobSummary | null;
}

function mapRenderStatus(status: string): StateVariant {
  const s = status.toLowerCase();
  if (s === "completed" || s === "done" || s === "success") return "success";
  if (s === "failed" || s === "error") return "danger";
  if (s === "processing" || s === "rendering" || s === "queued" || s === "pending")
    return "warning";
  return "info";
}

export function RenderStatus({ job }: RenderStatusProps) {
  if (!job) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Render Status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-400">No render job.</p>
        </CardContent>
      </Card>
    );
  }

  const variant = mapRenderStatus(job.status);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Render Status</CardTitle>
          <StatusIndicator
            state={variant}
            label={job.status}
            pulse={job.status === "processing" || job.status === "rendering" || job.status === "queued"}
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">Provider</span>
            <span className="font-medium text-gray-700">{job.provider}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">Created</span>
            <span className="text-gray-600">{new Date(job.created_at).toLocaleString()}</span>
          </div>
          {job.error_message && (
            <p className="text-sm text-red-600">{job.error_message}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
