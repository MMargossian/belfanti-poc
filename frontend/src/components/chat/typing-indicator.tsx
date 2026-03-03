export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      <span
        className="w-2 h-2 rounded-full bg-accent-blue animate-bounce-dot"
        style={{ animationDelay: "0s" }}
      />
      <span
        className="w-2 h-2 rounded-full bg-accent-blue animate-bounce-dot"
        style={{ animationDelay: "0.16s" }}
      />
      <span
        className="w-2 h-2 rounded-full bg-accent-blue animate-bounce-dot"
        style={{ animationDelay: "0.32s" }}
      />
    </div>
  );
}
