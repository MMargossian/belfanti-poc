"use client";

import { useState } from "react";
import { ShieldCheck, Check, MessageSquare, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { QuoteReview } from "./quote-review";
import { EmailReview } from "./email-review";
import type { ApprovalGate } from "@/lib/types";

interface ApprovalDialogProps {
  gate: ApprovalGate;
  onSubmit: (decision: string, feedback: string) => void;
}

export function ApprovalDialog({ gate, onSubmit }: ApprovalDialogProps) {
  const [feedback, setFeedback] = useState("");
  const isQuote = gate.gate_name === "quote_review";

  return (
    <div className="mx-6 mb-4 rounded-xl glass glass-border border-accent-amber/30 overflow-hidden animate-scale-in flex flex-col max-h-[70vh]">
      {/* Header */}
      <div className="flex-shrink-0 bg-gradient-to-r from-accent-amber/20 via-accent-amber/10 to-transparent px-4 py-3 border-b border-accent-amber/20">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-accent-amber" />
          <h3 className="text-sm font-semibold text-accent-amber">
            {isQuote ? "Quote Review Required" : "Email Review Required"}
          </h3>
        </div>
        <p className="text-xs text-text-muted mt-0.5 ml-7">
          Review the details below and approve, request changes, or reject.
        </p>
      </div>

      {/* Scrollable content */}
      <div className="overflow-y-auto flex-1 min-h-0 p-4 bg-bg-elevated/60">
        {isQuote ? (
          <QuoteReview data={gate.gate_data} />
        ) : (
          <EmailReview data={gate.gate_data} />
        )}
      </div>

      {/* Fixed bottom: feedback + actions */}
      <div className="flex-shrink-0 p-4 pt-3 bg-bg-elevated/60 border-t border-border-subtle">
        {/* Feedback */}
        <div>
          <p className="text-xs text-text-muted mb-1.5">
            Feedback (required for reject/changes)
          </p>
          <Textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Add comments or instructions..."
            rows={2}
            className="resize-none"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-3">
          <Button
            variant="success"
            className="flex-[2] gap-1.5 hover:shadow-glow-green transition-shadow"
            onClick={() => onSubmit("approved", feedback)}
          >
            <Check className="w-4 h-4" />
            Approve
          </Button>
          <Button
            variant="warning"
            className="flex-1 gap-1.5"
            onClick={() => onSubmit("changes_requested", feedback)}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            Changes
          </Button>
          <Button
            variant="destructive"
            className="flex-1 gap-1.5"
            onClick={() => onSubmit("rejected", feedback)}
          >
            <X className="w-3.5 h-3.5" />
            Reject
          </Button>
        </div>
      </div>
    </div>
  );
}
