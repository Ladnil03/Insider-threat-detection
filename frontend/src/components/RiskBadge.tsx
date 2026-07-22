interface RiskBadgeProps {
  severity: "low" | "medium" | "high" | "critical";
}

const colors: Record<string, string> = {
  low: "bg-green-100 text-green-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-orange-100 text-orange-800",
  critical: "bg-red-100 text-red-800",
};

function RiskBadge({ severity }: RiskBadgeProps) {
  return (
    <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${colors[severity]}`}>
      {severity.toUpperCase()}
    </span>
  );
}

export default RiskBadge;
