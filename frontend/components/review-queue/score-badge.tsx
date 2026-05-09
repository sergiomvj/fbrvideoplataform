"use client";

import { Badge } from "@/components/ui/badge";
import type { BadgeVariant } from "@/components/ui/badge";

interface ScoreBadgeProps {
  score: number;
}

function getScoreVariant(score: number): BadgeVariant {
  if (score >= 90) return "success";
  if (score >= 60) return "warning";
  return "danger";
}

function getScoreLabel(score: number): string {
  if (score >= 90) return "Excellent";
  if (score >= 60) return "Acceptable";
  return "Low";
}

export function ScoreBadge({ score }: ScoreBadgeProps) {
  return (
    <Badge variant={getScoreVariant(score)}>
      {score}/100 &middot; {getScoreLabel(score)}
    </Badge>
  );
}
