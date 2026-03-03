"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { PipelineChip } from "./pipeline-chip";
import { PIPELINE_PHASES, PHASE_ICONS } from "@/lib/constants";
import type { PipelineState } from "@/lib/types";

interface PipelineViewProps {
  pipeline: PipelineState;
}

const TOTAL_STAGES = 20;

export function PipelineView({ pipeline }: PipelineViewProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const completedCount = pipeline.completed_stages.length;
  const progress = Math.round((completedCount / TOTAL_STAGES) * 100);

  function getStageStatus(stage: string): "completed" | "current" | "failed" | "pending" {
    if (stage === pipeline.failed_stage) return "failed";
    if (pipeline.completed_stages.includes(stage)) return "completed";
    if (stage === pipeline.current_stage) return "current";
    return "pending";
  }

  return (
    <div className="px-6 py-3 border-b border-border/50 flex-shrink-0">
      {/* Header row — always visible, clickable */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full mb-2 group"
      >
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-text-muted" />
          ) : (
            <ChevronRight className="w-4 h-4 text-text-muted" />
          )}
          <span className="text-sm font-medium text-text-primary">
            Pipeline Progress
          </span>
        </div>
        <span className="text-xs text-text-muted">
          {completedCount}/{TOTAL_STAGES} stages ({progress}%)
        </span>
      </button>

      {/* Progress bar — always visible */}
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-bg-secondary">
        <div
          className="h-full rounded-full shimmer-bar transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Phase details — collapsible */}
      {isExpanded && (
        <div className="space-y-3 mt-4 animate-fade-in">
          {PIPELINE_PHASES.map((phase) => {
            const PhaseIcon = PHASE_ICONS[phase.label];
            return (
              <div key={phase.label}>
                <div className="flex items-center gap-1.5 mb-1.5">
                  {PhaseIcon && (
                    <PhaseIcon className="w-3 h-3 text-text-muted" />
                  )}
                  <p className="text-xs text-text-muted">{phase.label}</p>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {phase.stages.map((stage) => (
                    <PipelineChip
                      key={stage}
                      stage={stage}
                      status={getStageStatus(stage)}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
