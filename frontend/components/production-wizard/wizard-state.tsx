"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

export type ProductionMode = "automatic" | "manual";

export interface Template {
  id: string;
  name: string;
  description?: string;
  variations: Variation[];
}

export interface Variation {
  id: string;
  name: string;
  description?: string;
}

export interface WizardData {
  mode: ProductionMode | null;
  template: Template | null;
  variation: Variation | null;
  title: string;
  base_content: string;
  editorial_context: string;
  restrictions: string;
}

interface WizardContextValue {
  data: WizardData;
  setData: React.Dispatch<React.SetStateAction<WizardData>>;
}

const initialData: WizardData = {
  mode: null,
  template: null,
  variation: null,
  title: "",
  base_content: "",
  editorial_context: "",
  restrictions: "",
};

const WizardContext = createContext<WizardContextValue | null>(null);

export function WizardProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<WizardData>(initialData);

  return (
    <WizardContext.Provider value={{ data, setData }}>
      {children}
    </WizardContext.Provider>
  );
}

export function useWizard() {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error("useWizard must be used within a WizardProvider");
  }
  return context;
}
