"use client";

import { Button } from "@/components/ui/button";

interface ReviewActionsProps {
  onApprove: () => void;
  onReject: () => void;
  onRequery: () => void;
  disabled?: boolean;
  processing?: boolean;
}

export function ReviewActions({ onApprove, onReject, onRequery, disabled, processing }: ReviewActionsProps) {
  return (
    <div className="flex gap-2">
      <Button
        onClick={onApprove}
        disabled={disabled || processing}
        variant="success"
        size="sm"
      >
        {processing ? "Processing..." : "Approve"}
      </Button>
      <Button
        onClick={onReject}
        disabled={disabled || processing}
        variant="danger"
        size="sm"
      >
        {processing ? "Processing..." : "Reject"}
      </Button>
      <Button
        onClick={onRequery}
        disabled={disabled || processing}
        variant="secondary"
        size="sm"
      >
        {processing ? "Processing..." : "Requery"}
      </Button>
    </div>
  );
}
