import { NextResponse } from "next/server";
import { getSession } from "@/lib/session";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";
const INTERNAL_TOKEN = process.env.INTERNAL_TOKEN || "";

interface FrontendVariation {
  id: string;
  name: string;
  description?: string;
}

interface FrontendTemplate {
  id: string;
  name: string;
  description?: string;
  variations: FrontendVariation[];
}

const FALLBACK_TEMPLATES: FrontendTemplate[] = [
  {
    id: "presenter-short",
    name: "Presenter Short",
    description:
      "Video vertical de ate 60 segundos com avatar apresentando o texto em fundo institucional.",
    variations: [
      {
        id: "presenter-short-v1",
        name: "Variation 1",
        description: "Abertura limpa e institucional para noticias curtas.",
      },
      {
        id: "presenter-short-v2",
        name: "Variation 2",
        description: "Headline mais forte para reforcar o gancho inicial.",
      },
      {
        id: "presenter-short-v3",
        name: "Variation 3",
        description: "Enquadramento mais dinamico para reduzir repeticao visual.",
      },
    ],
  },
  {
    id: "videodoc-narrated",
    name: "VideoDoc Narrated",
    description:
      "Video horizontal de ate 180 segundos com narracao, imagens e videos de apoio.",
    variations: [
      {
        id: "videodoc-narrated-v1",
        name: "Variation 1",
        description: "Abertura documental classica com foco em contexto.",
      },
      {
        id: "videodoc-narrated-v2",
        name: "Variation 2",
        description: "Estrutura com headline inicial e progressao mais ritmada.",
      },
      {
        id: "videodoc-narrated-v3",
        name: "Variation 3",
        description: "Tratamento visual mais marcado para destacar a thumb e a abertura.",
      },
    ],
  },
];

function normalizeTemplates(payload: unknown): FrontendTemplate[] {
  const items =
    Array.isArray(payload)
      ? payload
      : payload && typeof payload === "object" && "templates" in payload
        ? (payload as { templates?: unknown[] }).templates ?? []
        : [];

  if (!Array.isArray(items)) {
    return [];
  }

  const normalizedTemplates: FrontendTemplate[] = [];

  for (const item of items) {
      if (!item || typeof item !== "object") {
        continue;
      }

      const template = item as {
        id?: string;
        type_id?: string;
        name?: string;
        description?: string;
        variations?: Array<{
          id?: string;
          label?: string;
          name?: string;
          description?: string;
        }>;
      };

      const id = template.id ?? template.type_id;
      const name = template.name;

      if (!id || !name) {
        continue;
      }

      const variations: FrontendVariation[] = [];

      if (Array.isArray(template.variations)) {
        for (const variation of template.variations) {
          if (!variation?.id) {
            continue;
          }

          variations.push({
            id: variation.id,
            name: variation.name ?? variation.label ?? variation.id,
            description: variation.description,
          });
        }
      }

      normalizedTemplates.push({
        id,
        name,
        description: template.description,
        variations,
      });
    }

  return normalizedTemplates;
}

function getBackendCandidates(): string[] {
  const candidates = [
    BACKEND_URL,
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
  ];

  return [...new Set(candidates.map((value) => value.trim()).filter(Boolean))];
}

export async function GET() {
  const session = await getSession();

  if (!session.isLoggedIn || !session.userId) {
    return NextResponse.json({ error: "Authentication required" }, { status: 401 });
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-User-Id": session.userId,
    "X-Organization-Id": session.organizationId || "default",
  };

  if (INTERNAL_TOKEN) {
    headers["X-Internal-Token"] = INTERNAL_TOKEN;
  }

  const candidates = getBackendCandidates();
  const diagnostics: string[] = [];

  for (const baseUrl of candidates) {
    try {
      const response = await fetch(`${baseUrl}/templates/`, {
        method: "GET",
        headers,
        cache: "no-store",
      });

      if (response.status === 404) {
        diagnostics.push(`${baseUrl} -> 404`);
        continue;
      }

      const contentType = response.headers.get("content-type");
      if (contentType?.includes("application/json")) {
        const data = await response.json();
        if (!response.ok) {
          return NextResponse.json(data, { status: response.status });
        }

        const templates = normalizeTemplates(data);
        if (templates.length > 0) {
          return NextResponse.json(
            {
              templates,
              source: baseUrl,
              fallback: false,
            },
            { status: response.status }
          );
        }

        diagnostics.push(`${baseUrl} -> incompatible template payload`);
        continue;
      }

      return new NextResponse(response.body, {
        status: response.status,
        statusText: response.statusText,
      });
    } catch {
      diagnostics.push(`${baseUrl} -> unreachable`);
    }
  }

  return NextResponse.json(
    {
      templates: FALLBACK_TEMPLATES,
      warning:
        "Using local fallback templates because no compatible Synkra backend was found for /templates/.",
      fallback: true,
      diagnostics,
      configuredBackendUrl: BACKEND_URL,
    },
    { status: 200 }
  );
}
