"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { StatusIndicator } from "@/components/ui/status-indicator";
import type { StateVariant } from "@/lib/design-system/tokens";

interface RenderJob {
  id: string;
  status: string;
  progress: number;
  output_url?: string | null;
  error_message?: string | null;
}

interface RenderStatusProps {
  job: RenderJob | null;
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
          <p className="text-sm text-gray-400">No render job found.</p>
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
            <span className="text-gray-500">Progress</span>
            <span className="font-medium text-gray-700">{job.progress}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-gray-100">
            <div
              className={`h-2 rounded-full transition-all ${
                variant === "success"
                  ? "bg-green-500"
                  : variant === "danger"
                    ? "bg-red-500"
                    : "bg-amber-500"
              }`}
              style={{ width: `${Math.min(100, Math.max(0, job.progress))}%` }}
            />
          </div>
          {job.output_url && (
            <a
              href={job.output_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              View Output
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-4.5-4.5h6m0 0v6m0-6L9.75 14.25" />
              </svg>
            </a>
          )}
          {job.error_message && (
            <p className="text-sm text-red-600">{job.error_message}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
