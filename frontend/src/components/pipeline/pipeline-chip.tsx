import { CheckCircle2, Loader2, Circle, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import { STAGE_LABELS } from "@/lib/constants";

interface PipelineChipProps {
  stage: string;
  status: "completed" | "current" | "failed" | "pending";
}

const STATUS_ICONS = {
  completed: CheckCircle2,
  current: Loader2,
  failed: XCircle,
  pending: Circle,
};

export function PipelineChip({ stage, status }: PipelineChipProps) {
  const label = STAGE_LABELS[stage] || stage;
  const Icon = STATUS_ICONS[status];

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="animate-scale-in">
          <Badge
            variant={status}
            className={`gap-1 cursor-default ${
              status === "current" ? "shadow-glow-blue" : ""
            }`}
          >
            <Icon
              className={`w-3 h-3 ${
                status === "current" ? "animate-spin" : ""
              }`}
            />
            {label}
          </Badge>
        </div>
      </TooltipTrigger>
      <TooltipContent>
        <p>{stage.replace(/_/g, " ")}</p>
      </TooltipContent>
    </Tooltip>
  );
}
