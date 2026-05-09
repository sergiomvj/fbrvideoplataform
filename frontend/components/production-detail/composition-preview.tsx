"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface CompositionSlot {
  slot_type: string;
  duration: number;
  content: string;
}

interface CompositionPreviewProps {
  slots: CompositionSlot[];
}

export function CompositionPreview({ slots }: CompositionPreviewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Composition Preview</CardTitle>
      </CardHeader>
      <CardContent>
        {slots.length === 0 ? (
          <p className="text-sm text-gray-400">No composition slots defined.</p>
        ) : (
          <div className="space-y-2">
            <div className="grid grid-cols-[2fr_1fr_3fr] gap-2 border-b border-gray-200 pb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
              <span>Slot Type</span>
              <span>Duration</span>
              <span>Content</span>
            </div>
            {slots.map((slot, idx) => (
              <div
                key={`${slot.slot_type}-${idx}`}
                className="grid grid-cols-[2fr_1fr_3fr] gap-2 border-b border-gray-100 py-2 text-sm last:border-0"
              >
                <span className="font-medium text-gray-700">{slot.slot_type}</span>
                <span className="text-gray-600">{slot.duration}s</span>
                <span className="text-gray-600 truncate">{slot.content}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
