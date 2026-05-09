"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { WizardProvider, useWizard } from "@/components/production-wizard/wizard-state";
import { ModeStep } from "@/components/production-wizard/mode-step";
import { TemplateStep } from "@/components/production-wizard/template-step";
import { VariationStep } from "@/components/production-wizard/variation-step";
import { ContentStep } from "@/components/production-wizard/content-step";
import { AssetBindingStep } from "@/components/production-wizard/asset-binding-step";

const BASE_STEPS = ["Mode", "Template", "Variation", "Content"] as const;
const MANUAL_STEPS = [...BASE_STEPS, "Asset Binding"] as const;

type StepLabel = (typeof MANUAL_STEPS)[number];

type SubmitStatus = "idle" | "submitting" | "success" | "error";

function LoginForm({ onLoginSuccess }: { onLoginSuccess: () => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/auth/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setError(body.error || "Login failed");
        return;
      }

      onLoginSuccess();
    } catch {
      setError("Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm py-16 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">Authentication Required</h1>
        <p className="text-sm text-gray-500 mt-2">Please log in first.</p>
      </div>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Logging in..." : "Log In"}
          </Button>
        </form>
      </Card>
    </div>
  );
}

function WizardContent() {
  const { data } = useWizard();
  const [currentStep, setCurrentStep] = useState(0);
  const [submitStatus, setSubmitStatus] = useState<SubmitStatus>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [productionId, setProductionId] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  const isManual = data.mode === "manual";
  const steps: readonly StepLabel[] = isManual ? MANUAL_STEPS : BASE_STEPS;

  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch("/api/auth/session", { method: "GET" });
        if (res.ok) {
          const body = await res.json();
          setIsAuthenticated(body.isLoggedIn === true);
        } else {
          setIsAuthenticated(false);
        }
      } catch {
        setIsAuthenticated(false);
      }
    }
    checkSession();
  }, []);

  if (isAuthenticated === null) {
    return (
      <div className="mx-auto max-w-3xl py-16 text-center text-sm text-gray-500">
        Checking authentication...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  async function handleSubmit() {
    setSubmitStatus("submitting");
    setErrorMessage("");

    try {
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
      const pid = result.id ?? result.production_id ?? "unknown";
      setProductionId(pid);

      if (isManual && data.bindings.length > 0) {
        for (const binding of data.bindings) {
          if (!binding.assetReference.trim()) continue;
          const restrictions = binding.restrictions
            .split(",")
            .map((s) => s.trim())
            .filter((s) => s.length > 0);
          const bindingRes = await fetch(`/api/productions/${pid}/bindings`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              production_id: pid,
              scene_index: binding.sceneIndex,
              asset_reference: binding.assetReference,
              asset_type: binding.assetType,
              restrictions,
            }),
          });
          if (!bindingRes.ok) {
            const body = await bindingRes.json().catch(() => ({}));
            throw new Error(body.error || `Binding failed with status ${bindingRes.status}`);
          }
        }
      }

      setSubmitStatus("success");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "An unexpected error occurred");
      setSubmitStatus("error");
    }
  }

  function canGoNext(): boolean {
    switch (steps[currentStep]) {
      case "Mode":
        return data.mode !== null;
      case "Template":
        return data.template !== null;
      case "Variation":
        return true;
      case "Content":
        return data.title.trim().length > 0;
      case "Asset Binding":
        return true;
      default:
        return false;
    }
  }

  function goNext() {
    if (currentStep < steps.length - 1 && canGoNext()) {
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
          {steps.map((label, idx) => (
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
              {idx < steps.length - 1 && (
                <div className={`h-0.5 w-6 ${idx < currentStep ? "bg-blue-400" : "bg-gray-200"}`} />
              )}
            </li>
          ))}
        </ol>
      </nav>

      <Card className="p-6">
        {steps[currentStep] === "Mode" && <ModeStep />}
        {steps[currentStep] === "Template" && <TemplateStep />}
        {steps[currentStep] === "Variation" && <VariationStep />}
        {steps[currentStep] === "Content" && <ContentStep />}
        {steps[currentStep] === "Asset Binding" && <AssetBindingStep />}
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

        {currentStep < steps.length - 1 ? (
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
