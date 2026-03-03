"use client";

import { useState, useCallback } from "react";
import type { PipelineState } from "@/lib/types";

const DEFAULT_PIPELINE: PipelineState = {
  current_stage: "rfq_received",
  completed_stages: [],
  failed_stage: null,
  error_message: null,
};

export function usePipeline() {
  const [pipeline, setPipeline] = useState<PipelineState>(DEFAULT_PIPELINE);

  const updatePipeline = useCallback((data: PipelineState) => {
    setPipeline(data);
  }, []);

  const resetPipeline = useCallback(() => {
    setPipeline(DEFAULT_PIPELINE);
  }, []);

  return { pipeline, updatePipeline, resetPipeline };
}
