"use client";

import { Button } from "@/components/ui/button";

interface ReviewActionsProps {
  onApprove: () => void;
  onReject: () => void;
  onRequery: () => void;
  disabled?: boolean;
}

export function ReviewActions({ onApprove, onReject, onRequery, disabled }: ReviewActionsProps) {
  return (
    <div className="flex items-center gap-2">
      <Button variant="primary" size="sm" onClick={onApprove} disabled={disabled}>
        Approve
      </Button>
      <Button variant="danger" size="sm" onClick={onReject} disabled={disabled}>
        Reject
      </Button>
      <Button variant="secondary" size="sm" onClick={onRequery} disabled={disabled}>
        Requery
      </Button>
    </div>
  );
}
