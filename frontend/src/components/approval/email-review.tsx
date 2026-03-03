import { Paperclip } from "lucide-react";

interface EmailReviewProps {
  data: Record<string, unknown>;
}

export function EmailReview({ data }: EmailReviewProps) {
  const to = (data.to as string) || "";
  const subject = (data.subject as string) || "";
  const preview = (data.preview as string) || "";
  const attachments = (data.attachments as string[]) || [];

  return (
    <div className="space-y-3">
      <div className="flex justify-between">
        <span className="text-sm text-text-secondary">To</span>
        <span className="text-sm text-text-primary font-medium">{to}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-sm text-text-secondary">Subject</span>
        <span className="text-sm text-text-primary">{subject}</span>
      </div>
      {preview && (
        <div>
          <p className="text-xs text-text-muted mb-1">Preview</p>
          <div className="bg-bg-secondary/60 p-3 rounded-lg border border-border-subtle/50 text-sm text-text-secondary whitespace-pre-wrap font-mono">
            {preview}
          </div>
        </div>
      )}
      {attachments.length > 0 && (
        <div>
          <p className="text-xs text-text-muted mb-1">Attachments</p>
          <div className="flex flex-wrap gap-1.5">
            {attachments.map((a, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 text-xs bg-bg-hover/80 px-2.5 py-1 rounded-md text-text-secondary border border-border-subtle/50"
              >
                <Paperclip className="w-3 h-3 text-text-muted" />
                {a}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
