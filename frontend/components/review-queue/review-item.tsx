"use client";

import Image from "next/image";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { ScoreBadge } from "./score-badge";
import { ReviewActions } from "./review-actions";

export interface ReviewItemData {
  id: string;
  production_id: string;
  scene_id: string;
  scene_index: number;
  scene_label: string;
  asset_id: string;
  asset_url: string;
  asset_type: string;
  source: string;
  score: number;
  justification: string;
  decision: string;
  status: "pending" | "approved" | "rejected" | "requeried";
  preview_url: string;
}

interface ReviewItemProps {
  item: ReviewItemData;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  onRequery: (id: string) => void;
  processing?: boolean;
}

export function ReviewItem({ item, onApprove, onReject, onRequery, processing }: ReviewItemProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            Scene {item.scene_index}: {item.scene_label}
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">{item.source}</span>
            <ScoreBadge score={item.score} />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex gap-4">
          <div className="flex h-32 w-48 shrink-0 items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 overflow-hidden">
            {item.preview_url ? (
              <Image
                src={item.preview_url}
                alt={`Preview for ${item.scene_label}`}
                fill
                className="object-cover"
                unoptimized
              />
            ) : (
              <span className="text-xs text-gray-400">Asset Preview</span>
            )}
          </div>
          <div className="flex-1 space-y-2">
            <p className="text-sm font-medium text-gray-700">Justification</p>
            <p className="text-sm text-gray-600">{item.justification}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs text-gray-400">Type: {item.asset_type || "unknown"}</span>
              <span className="text-xs text-gray-400">|</span>
              <span className="text-xs text-gray-400">ID: {item.asset_id}</span>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="justify-between">
        <span className="text-xs text-gray-400">ID: {item.id}</span>
        <ReviewActions
          onApprove={() => onApprove(item.id)}
          onReject={() => onReject(item.id)}
          onRequery={() => onRequery(item.id)}
          disabled={processing}
          processing={processing}
        />
      </CardFooter>
    </Card>
  );
}
