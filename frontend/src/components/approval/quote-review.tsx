import { formatCurrency } from "@/lib/utils";

interface QuoteReviewProps {
  data: Record<string, unknown>;
}

export function QuoteReview({ data }: QuoteReviewProps) {
  const summary = (data.summary as string) || "";
  const total = (data.total as number) || 0;
  const customer = (data.customer as string) || "";
  const lineItems = (data.line_items as Record<string, unknown>[]) || [];

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <span className="text-sm text-text-secondary">Customer</span>
        <span className="text-sm font-medium text-text-primary">{customer}</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-sm text-text-secondary">Total</span>
        <span className="text-lg font-bold text-accent-green shadow-glow-green rounded px-1">
          {formatCurrency(total)}
        </span>
      </div>
      {summary && (
        <p className="text-sm text-text-secondary bg-bg-secondary/60 p-2.5 rounded-lg border border-border-subtle/50">
          {summary}
        </p>
      )}
      {lineItems.length > 0 && (
        <div className="border border-border-subtle/50 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg-secondary/80">
                <th className="text-left p-2.5 text-text-muted font-medium">Part</th>
                <th className="text-right p-2.5 text-text-muted font-medium">Qty</th>
                <th className="text-right p-2.5 text-text-muted font-medium">Price</th>
              </tr>
            </thead>
            <tbody>
              {lineItems.map((item, i) => (
                <tr
                  key={i}
                  className={`border-t border-border-subtle/50 ${
                    i % 2 === 1 ? "bg-bg-secondary/30" : ""
                  }`}
                >
                  <td className="p-2.5 text-text-primary">
                    {(item.part_name as string) || (item.part_number as string) || `Item ${i + 1}`}
                  </td>
                  <td className="p-2.5 text-right text-text-secondary">
                    {(item.quantity as number) || "-"}
                  </td>
                  <td className="p-2.5 text-right text-text-primary font-medium">
                    {(() => {
                      const price = (item.line_total ?? item.total_price ?? item.price ?? item.total ?? item.unit_price) as number | undefined;
                      return price != null && !isNaN(price) ? formatCurrency(price) : "-";
                    })()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
