"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface CompositionSlot {
  slot_index: number;
  slot_type: string;
  duration_seconds: number;
  content_reference: string;
  asset_url: string | null;
}

interface CompositionSummary {
  id: string;
  template_type_id: string;
  variation_id: string;
  total_duration_seconds: number;
  slots: CompositionSlot[];
}

interface CompositionPreviewProps {
  composition: CompositionSummary | null;
}

export function CompositionPreview({ composition }: CompositionPreviewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Composition Preview</CardTitle>
      </CardHeader>
      <CardContent>
        {!composition ? (
          <p className="text-sm text-gray-400">No composition yet.</p>
        ) : composition.slots.length === 0 ? (
          <p className="text-sm text-gray-400">No composition slots defined.</p>
        ) : (
          <div className="space-y-2">
            <div className="grid grid-cols-[2fr_1fr_3fr] gap-2 border-b border-gray-200 pb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
              <span>Slot Type</span>
              <span>Duration</span>
              <span>Content</span>
            </div>
            {composition.slots.map((slot) => (
              <div
                key={`slot-${slot.slot_index}`}
                className="grid grid-cols-[2fr_1fr_3fr] gap-2 border-b border-gray-100 py-2 text-sm last:border-0"
              >
                <span className="font-medium text-gray-700">{slot.slot_type}</span>
                <span className="text-gray-600">{slot.duration_seconds}s</span>
                <span className="text-gray-600 truncate">{slot.content_reference}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
