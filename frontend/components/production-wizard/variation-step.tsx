"use client";

import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useWizard } from "./wizard-state";

export function VariationStep() {
  const { data, setData } = useWizard();
  const variations = data.template?.variations ?? [];

  if (variations.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-sm text-gray-500">No variations available for this template. You can skip this step.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Select a Variation</h2>
        <p className="text-sm text-gray-500 mt-1">Choose the variation for the &ldquo;{data.template?.name}&rdquo; template.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {variations.map((variation) => {
          const isSelected = data.variation?.id === variation.id;

          return (
            <Card
              key={variation.id}
              className={`cursor-pointer transition-all hover:shadow-md ${isSelected ? "ring-2 ring-blue-600 border-blue-600" : "hover:border-gray-300"}`}
              onClick={() => setData((prev) => ({ ...prev, variation }))}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{variation.name}</CardTitle>
                  {isSelected && <Badge variant="success">Selected</Badge>}
                </div>
                {variation.description && (
                  <CardDescription className="mt-1">{variation.description}</CardDescription>
                )}
              </CardHeader>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
