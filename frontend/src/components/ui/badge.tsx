import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-bg-elevated text-text-secondary border border-border",
        completed: "bg-accent-green/15 text-accent-green border border-accent-green/30",
        current: "bg-accent-blue/15 text-accent-blue border border-accent-blue/30",
        failed: "bg-accent-red/15 text-accent-red border border-accent-red/30",
        pending: "bg-bg-secondary text-text-muted border border-border-subtle",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
