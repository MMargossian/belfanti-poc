"use client";

import { useState, useEffect } from "react";
import { Factory, RotateCcw, ChevronRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getModules, updateModules, loadDemo } from "@/lib/api";
import { MODULE_GROUPS, MODULE_ICONS, DEMO_RFQS } from "@/lib/constants";
import type { ModuleInfo } from "@/lib/types";

interface SidebarProps {
  sessionId: string;
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  onDemoLoad: (message: string) => void;
  onReset: () => void;
}

export function Sidebar({
  sessionId,
  apiKey,
  onApiKeyChange,
  onDemoLoad,
  onReset,
}: SidebarProps) {
  const [keyInput, setKeyInput] = useState(apiKey);
  const [modules, setModules] = useState<ModuleInfo[]>([]);

  useEffect(() => {
    if (sessionId) {
      getModules(sessionId).then(setModules).catch(() => {});
    }
  }, [sessionId]);

  const handleKeySubmit = () => {
    if (keyInput.trim()) {
      onApiKeyChange(keyInput.trim());
    }
  };

  const handleModuleToggle = async (moduleName: string, enabled: boolean) => {
    const updated = modules.map((m) =>
      m.name === moduleName ? { ...m, enabled } : m
    );
    setModules(updated);
    const enabledNames = updated.filter((m) => m.enabled).map((m) => m.name);
    await updateModules(sessionId, enabledNames);
  };

  const handleDemoClick = async (index: number) => {
    try {
      const data = await loadDemo(sessionId, index);
      onDemoLoad(data.message);
    } catch {
      // ignore
    }
  };

  const hasKey = apiKey.length > 0;

  return (
    <div className="w-72 h-screen glass glass-border flex flex-col border-r border-border/50">
      {/* Branding */}
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center gap-2.5 mb-1">
          <div className="p-1.5 rounded-lg bg-accent-blue/10 border border-accent-blue/20">
            <Factory className="w-5 h-5 text-accent-blue" />
          </div>
          <span className="text-lg font-bold text-text-primary">Belfanti CNC</span>
        </div>
        <p className="text-xs text-text-muted ml-10">Manufacturing Order Pipeline</p>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-5">
          {/* API Key */}
          <div>
            <label className="text-xs font-medium text-text-secondary uppercase tracking-wider flex items-center gap-2 mb-2">
              API Key
              <span
                className={`inline-block w-2 h-2 rounded-full ${
                  hasKey
                    ? "bg-accent-green animate-pulse-glow"
                    : "bg-accent-amber animate-pulse-glow"
                }`}
              />
            </label>
            <div className="flex gap-2">
              <Input
                type="password"
                placeholder="sk-ant-..."
                value={keyInput}
                onChange={(e) => setKeyInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleKeySubmit()}
                className="text-xs"
              />
              <Button size="sm" onClick={handleKeySubmit} variant="secondary">
                Set
              </Button>
            </div>
          </div>

          <Separator className="bg-border/50" />

          {/* Modules */}
          <div>
            <p className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
              Modules
            </p>
            <div className="space-y-4">
              {MODULE_GROUPS.map((group) => {
                const GroupIcon = MODULE_ICONS[group.label];
                return (
                  <div key={group.label}>
                    <div className="flex items-center gap-1.5 mb-2">
                      {GroupIcon && (
                        <GroupIcon className="w-3.5 h-3.5 text-text-muted" />
                      )}
                      <p className="text-xs text-text-muted">{group.label}</p>
                    </div>
                    <div className="space-y-2">
                      {group.modules.map((modName) => {
                        const mod = modules.find((m) => m.name === modName);
                        if (!mod) return null;
                        return (
                          <div
                            key={mod.name}
                            className="flex items-center justify-between group"
                          >
                            <span className="text-sm text-text-primary group-hover:text-accent-blue transition-colors">
                              {mod.label}
                            </span>
                            <Switch
                              checked={mod.enabled}
                              onCheckedChange={(checked) =>
                                handleModuleToggle(mod.name, checked)
                              }
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <Separator className="bg-border/50" />

          {/* Demo RFQs */}
          <div>
            <p className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
              Sample RFQs
            </p>
            <div className="space-y-2">
              {DEMO_RFQS.map((demo) => (
                <button
                  key={demo.index}
                  onClick={() => handleDemoClick(demo.index)}
                  className="w-full text-left p-3 rounded-lg glass glass-border hover:bg-bg-hover/60 hover:border-accent-blue/30 transition-all duration-200 group"
                >
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-text-primary group-hover:text-accent-blue transition-colors">
                      {demo.label}
                    </p>
                    <ChevronRight className="w-3.5 h-3.5 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <p className="text-xs text-text-muted mt-0.5">
                    {demo.description}
                  </p>
                </button>
              ))}
            </div>
          </div>

          <Separator className="bg-border/50" />

          {/* Reset */}
          <Button
            variant="outline"
            className="w-full text-accent-red border-accent-red/30 hover:bg-accent-red/10 gap-2"
            onClick={onReset}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset Session
          </Button>
        </div>
      </ScrollArea>
    </div>
  );
}
