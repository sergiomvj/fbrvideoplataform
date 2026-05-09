"use client";

import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useWizard, type ProductionMode } from "./wizard-state";

const modes: { value: ProductionMode; title: string; description: string; badge: string }[] = [
  {
    value: "automatic",
    title: "Automatic",
    description: "AI generates content variations based on your template and editorial context. Fastest workflow for scaled production.",
    badge: "Recommended",
  },
  {
    value: "manual",
    title: "Manual",
    description: "You craft each variation yourself with full creative control. Best for bespoke or high-stakes content.",
    badge: "Full Control",
  },
];

export function ModeStep() {
  const { data, setData } = useWizard();

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Choose Production Mode</h2>
        <p className="text-sm text-gray-500 mt-1">Select how your production content will be generated.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {modes.map((mode) => {
          const isSelected = data.mode === mode.value;

          return (
            <Card
              key={mode.value}
              className={`cursor-pointer transition-all hover:shadow-md ${isSelected ? "ring-2 ring-blue-600 border-blue-600" : "hover:border-gray-300"}`}
              onClick={() => setData((prev) => ({ ...prev, mode: mode.value }))}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{mode.title}</CardTitle>
                  <Badge variant={mode.value === "automatic" ? "info" : "neutral"}>
                    {mode.badge}
                  </Badge>
                </div>
                <CardDescription className="mt-2">{mode.description}</CardDescription>
              </CardHeader>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
