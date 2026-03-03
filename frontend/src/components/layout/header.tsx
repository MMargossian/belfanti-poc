import { Bot } from "lucide-react";

export function Header() {
  return (
    <div className="px-6 py-4 border-b border-border/50 bg-gradient-to-r from-bg-secondary/50 to-transparent">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Bot className="w-6 h-6 text-accent-blue" />
          <h1 className="text-2xl font-bold text-text-primary">
            AI-Powered Order Pipeline
          </h1>
        </div>
        <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-accent-blue/10 text-accent-blue border border-accent-blue/20 shadow-glow-blue">
          AI Powered
        </span>
      </div>
      <p className="text-sm text-text-muted mt-0.5 ml-8">From RFQ to Work Order</p>
    </div>
  );
}
