"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useWizard, type Template } from "./wizard-state";

export function TemplateStep() {
  const { data, setData } = useWizard();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchTemplates() {
      try {
        const res = await fetch("/api/templates/", { cache: "no-store" });
        if (!res.ok) {
          const body = await res.json().catch(() => null);
          const backendMessage =
            body && typeof body === "object" && "error" in body && typeof body.error === "string"
              ? body.error
              : null;
          let message = backendMessage || `Failed to fetch templates (${res.status})`;

          if (res.status === 401) {
            message = backendMessage || "Authentication required. Reload the page and log in again.";
          } else if (res.status === 404) {
            message =
              backendMessage ||
              "Templates endpoint was not resolved. Check whether the Synkra backend is running on the configured port.";
          }

          throw new Error(message);
        }
        const json = await res.json();
        const items: Template[] = Array.isArray(json) ? json : json.templates ?? json.data ?? [];
        setTemplates(items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    fetchTemplates();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-sm text-gray-500">Loading templates...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 space-y-3">
        <p className="text-sm text-red-600">{error}</p>
        <Button variant="secondary" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </div>
    );
  }

  if (templates.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-sm text-gray-500">No templates available. Please create a template first.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Select a Template</h2>
        <p className="text-sm text-gray-500 mt-1">Choose the template that will define your production structure.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((template) => {
          const isSelected = data.template?.id === template.id;

          return (
            <Card
              key={template.id}
              className={`cursor-pointer transition-all hover:shadow-md ${isSelected ? "ring-2 ring-blue-600 border-blue-600" : "hover:border-gray-300"}`}
              onClick={() =>
                setData((prev) => ({
                  ...prev,
                  template,
                  variation: null,
                }))
              }
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{template.name}</CardTitle>
                  {template.variations?.length > 0 && (
                    <Badge variant="neutral">
                      {template.variations.length} variation{template.variations.length !== 1 ? "s" : ""}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              {template.description && (
                <CardContent>
                  <CardDescription>{template.description}</CardDescription>
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
