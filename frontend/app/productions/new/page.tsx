"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { WizardProvider, useWizard } from "@/components/production-wizard/wizard-state";
import { ModeStep } from "@/components/production-wizard/mode-step";
import { TemplateStep } from "@/components/production-wizard/template-step";
import { VariationStep } from "@/components/production-wizard/variation-step";
import { ContentStep } from "@/components/production-wizard/content-step";

const STEPS = ["Mode", "Template", "Variation", "Content"] as const;

type SubmitStatus = "idle" | "submitting" | "success" | "error";

function WizardContent() {
  const { data } = useWizard();
  const [currentStep, setCurrentStep] = useState(0);
  const [submitStatus, setSubmitStatus] = useState<SubmitStatus>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [productionId, setProductionId] = useState<string | null>(null);

  async function handleLogin() {
    const res = await fetch("/api/auth/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId: "current-user" }),
    });
    if (!res.ok) throw new Error("Login failed");
  }

  async function handleSubmit() {
    setSubmitStatus("submitting");
    setErrorMessage("");

    try {
      await handleLogin();

      const payload = {
        title: data.title,
        template_type_id: data.template?.id,
        variation_id: data.variation?.id ?? null,
        mode: data.mode,
        base_content: data.base_content,
        editorial_context: data.editorial_context,
        restrictions: data.restrictions,
      };

      const res = await fetch("/api/productions/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || `Request failed with status ${res.status}`);
      }

      const result = await res.json();
      setProductionId(result.id ?? result.production_id ?? "unknown");
      setSubmitStatus("success");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "An unexpected error occurred");
      setSubmitStatus("error");
    }
  }

  function canGoNext(): boolean {
    switch (currentStep) {
      case 0:
        return data.mode !== null;
      case 1:
        return data.template !== null;
      case 2:
        return true;
      case 3:
        return data.title.trim().length > 0;
      default:
        return false;
    }
  }

  function goNext() {
    if (currentStep < STEPS.length - 1 && canGoNext()) {
      setCurrentStep((s) => s + 1);
    }
  }

  function goBack() {
    if (currentStep > 0) {
      setCurrentStep((s) => s - 1);
    }
  }

  if (submitStatus === "success") {
    return (
      <div className="mx-auto max-w-2xl text-center py-16 space-y-4">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Production Created</h2>
        <p className="text-sm text-gray-500">Your production &ldquo;{data.title}&rdquo; has been created successfully.</p>
        {productionId && (
          <a
            href={`/productions/${productionId}`}
            className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
          >
            View production details
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </a>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">New Production</h1>
        <p className="text-sm text-gray-500 mt-1">Follow the steps below to create a new production.</p>
      </div>

      <nav aria-label="Progress">
        <ol className="flex items-center gap-2">
          {STEPS.map((label, idx) => (
            <li key={label} className="flex items-center gap-2">
              <div
                className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                  idx === currentStep
                    ? "bg-blue-600 text-white"
                    : idx < currentStep
                      ? "bg-blue-100 text-blue-700"
                      : "bg-gray-100 text-gray-500"
                }`}
              >
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-white/20 text-[10px] font-bold">
                  {idx < currentStep ? (
                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  ) : (
                    idx + 1
                  )}
                </span>
                {label}
              </div>
              {idx < STEPS.length - 1 && (
                <div className={`h-0.5 w-6 ${idx < currentStep ? "bg-blue-400" : "bg-gray-200"}`} />
              )}
            </li>
          ))}
        </ol>
      </nav>

      <Card className="p-6">
        {currentStep === 0 && <ModeStep />}
        {currentStep === 1 && <TemplateStep />}
        {currentStep === 2 && <VariationStep />}
        {currentStep === 3 && <ContentStep />}
      </Card>

      {submitStatus === "error" && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {errorMessage}
        </div>
      )}

      <div className="flex items-center justify-between">
        <Button
          variant="secondary"
          onClick={goBack}
          disabled={currentStep === 0}
        >
          Back
        </Button>

        {currentStep < STEPS.length - 1 ? (
          <Button onClick={goNext} disabled={!canGoNext()}>
            Next
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={!canGoNext() || submitStatus === "submitting"}
          >
            {submitStatus === "submitting" ? (
              <>
                <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                Creating...
              </>
            ) : (
              "Create Production"
            )}
          </Button>
        )}
      </div>
    </div>
  );
}

export default function NewProductionPage() {
  return (
    <WizardProvider>
      <WizardContent />
    </WizardProvider>
  );
}
