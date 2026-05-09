"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ReviewItem, type ReviewItemData } from "@/components/review-queue/review-item";

function ReviewPageContent() {
  const searchParams = useSearchParams();
  const productionId = searchParams.get("production_id") ?? "";

  const [items, setItems] = useState<ReviewItemData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    if (!productionId) {
      setLoading(false);
      setError("Missing production_id query parameter");
      return;
    }

    async function fetchQueue() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/review/${productionId}`);
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
  }, [productionId]);

  async function handleAction(id: string, action: "approve" | "reject" | "requery") {
    setProcessingId(id);
    try {
      const res = await fetch(`/api/review/${productionId}/${id}/${action}`, { method: "POST" });
      if (!res.ok) throw new Error(`Action failed (${res.status})`);
      const updated = await res.json();
      setItems((prev) =>
        prev.map((item) => (item.id === id ? { ...item, ...updated } : item))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process action");
    } finally {
      setProcessingId(null);
    }
  }
  }

  const pendingCount = items.filter((i) => i.status === "pending").length;
  const resolvedCount = items.filter((i) => i.status !== "pending").length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Review Queue</h1>
          <p className="text-sm text-gray-500 mt-1">
            Review and approve or reject queued items
          </p>
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

      {!loading && items.length === 0 && !error && (
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

export default function ReviewPage() {
  return (
    <Suspense
      fallback={
        <Card>
          <CardContent className="py-12 text-center text-sm text-gray-500">
            Loading...
          </CardContent>
        </Card>
      }
    >
      <ReviewPageContent />
    </Suspense>
  );
}
