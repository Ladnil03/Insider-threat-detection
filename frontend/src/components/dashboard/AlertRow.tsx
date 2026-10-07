import React from 'react';
import { cn } from 'cn';
import { Badge } from '../ui/badge';
import { Card } from '../ui/card';
import { Alert, SEVERITY_META } from '../../lib/dashboardData';

interface AlertRowProps {
  alert: Alert;
  onOpen: (alert: Alert) => void;
}

export const AlertRow: React.FC<AlertRowProps> = ({ alert, onOpen }) => {
  const meta = SEVERITY_META[alert.severity];

  return (
    <button
      type="button"
      onClick={() => onOpen(alert)}
      aria-label={`Open alert ${alert.id}`}
      className="w-full rounded-xl text-left outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
    >
      <Card
        className={cn(
          'gap-1.5 border-l-4 py-3 pr-3 pl-4 transition-colors hover:bg-muted/60',
          meta.border,
          alert.severity === 'critical' && 'glow-critical'
        )}
      >
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <Badge
            variant="outline"
            className={cn('border-border/80 bg-transparent', meta.text)}
          >
            <span className={cn('size-1.5 rounded-full', meta.dot)} />
            <span className="font-mono">{alert.score.toFixed(2)}</span>
            <span>{meta.label}</span>
          </Badge>
          <span className="font-mono text-xs text-muted-foreground">{alert.userId}</span>
          <span className="font-mono text-xs text-muted-foreground">{alert.time}</span>
          <span className="ml-auto flex gap-1">
            {alert.models.map((m) => (
              <span
                key={m}
                className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground"
              >
                {m}
              </span>
            ))}
          </span>
        </div>
        <p className="truncate text-sm text-foreground/90">{alert.headline}</p>
      </Card>
    </button>
  );
};

export default AlertRow;
