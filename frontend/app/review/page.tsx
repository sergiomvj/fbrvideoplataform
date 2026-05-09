"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ReviewItem, type ReviewItemData } from "@/components/review-queue/review-item";

type ReviewStatus = "pending" | "approved" | "rejected";

export default function ReviewPage() {
  const [items, setItems] = useState<ReviewItemData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [productionId, setProductionId] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const pid = params.get("production_id");
    setProductionId(pid);

    async function fetchQueue() {
      setLoading(true);
      setError(null);
      try {
        const url = pid ? `/api/review/${pid}` : "/api/review";
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Failed to load review queue (${res.status})`);
        const data = await res.json();
        setItems(Array.isArray(data) ? data : data.items ?? []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    fetchQueue();
  }, []);

  async function handleAction(id: string, action: "approve" | "reject" | "requery") {
    setProcessingId(id);
    try {
      const res = await fetch(`/api/review/${id}/${action}`, { method: "POST" });
      if (!res.ok) throw new Error(`Action failed (${res.status})`);
      setItems((prev) =>
        prev.map((item) => {
          if (item.id !== id) return item;
          const nextStatus: Record<string, ReviewStatus> = {
            approve: "approved",
            reject: "rejected",
            requery: "pending",
          };
          return { ...item, status: nextStatus[action] ?? item.status };
        })
      );
    } catch {
      setError("Failed to process action");
    } finally {
      setProcessingId(null);
    }
  }

  const pendingCount = items.filter((i) => i.status === "pending").length;
  const resolvedCount = items.filter((i) => i.status !== "pending").length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Review Queue</h1>
          {productionId && (
            <p className="text-sm text-gray-500 mt-1">
              Production: {productionId}
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="warning">{pendingCount} Pending</Badge>
          <Badge variant="success">{resolvedCount} Resolved</Badge>
        </div>
      </div>

      {loading && (
        <Card>
          <CardContent className="py-12 text-center text-sm text-gray-500">
            Loading review queue...
          </CardContent>
        </Card>
      )}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && items.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-sm text-gray-500">
            No items in the review queue.
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {items.map((item) => (
          <ReviewItem
            key={item.id}
            item={item}
            onApprove={(id) => handleAction(id, "approve")}
            onReject={(id) => handleAction(id, "reject")}
            onRequery={(id) => handleAction(id, "requery")}
            processing={processingId === item.id}
          />
        ))}
      </div>
    </div>
  );
}
