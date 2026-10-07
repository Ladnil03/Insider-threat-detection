import React from 'react';
import { cn } from 'cn';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '../ui/tooltip';
import { Button } from '../ui/button';
import { Alert, SEVERITY_META } from '../../lib/dashboardData';

export type AlertAction = 'acknowledge' | 'escalate' | 'false-positive';

interface AlertDetailDialogProps {
  alert: Alert | null;
  onOpenChange: (open: boolean) => void;
  onAction: (alert: Alert, action: AlertAction) => void;
}

const fmtAttribution = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(2)}`;

export const AlertDetailDialog: React.FC<AlertDetailDialogProps> = ({
  alert,
  onOpenChange,
  onAction,
}) => {
  const meta = alert ? SEVERITY_META[alert.severity] : null;

  return (
    <Dialog open={!!alert} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        {alert && meta && (
          <>
            <DialogHeader>
              <DialogTitle className="pr-6">{alert.headline}</DialogTitle>
              <DialogDescription className="flex items-center gap-2 pt-1">
                <Badge variant="outline" className={cn('bg-transparent', meta.text)}>
                  <span className={cn('size-1.5 rounded-full', meta.dot)} />
                  <span className="font-mono">{alert.score.toFixed(2)}</span>
                  <span>{meta.label}</span>
                </Badge>
                <span className="font-mono text-xs">{alert.id}</span>
              </DialogDescription>
            </DialogHeader>

            <Separator />

            <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              <div>
                <dt className="text-xs text-muted-foreground">Timestamp</dt>
                <dd className="font-mono text-xs text-foreground">{alert.time}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground">User ID</dt>
                <dd className="font-mono text-xs text-foreground">{alert.userId}</dd>
              </div>
              <div className="col-span-2">
                <dt className="text-xs text-muted-foreground">Flagged by</dt>
                <dd className="mt-1 flex gap-1">
                  {alert.models.map((m) => (
                    <span
                      key={m}
                      className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px] text-foreground/80"
                    >
                      {m}
                    </span>
                  ))}
                </dd>
              </div>
            </dl>

            <Separator />

            <div className="flex flex-col gap-2.5">
              <p className="text-xs text-muted-foreground">Top contributing features</p>
              {alert.shap.slice(0, 3).map((f) => (
                <Tooltip key={f.label}>
                  <TooltipTrigger asChild>
                    <div className="flex cursor-default items-start justify-between gap-3 rounded-md border border-border/60 bg-muted/40 px-3 py-2">
                      <span className="text-sm text-foreground">{f.label}</span>
                      <span className="shrink-0 font-mono text-xs text-muted-foreground">
                        {fmtAttribution(f.attribution)}
                      </span>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    SHAP contribution {fmtAttribution(f.attribution)} to the SAI score
                  </TooltipContent>
                </Tooltip>
              ))}
            </div>

            <DialogFooter className="gap-2 pt-1 sm:justify-start">
              <Button onClick={() => onAction(alert, 'acknowledge')}>Acknowledge</Button>
              <Button variant="destructive" onClick={() => onAction(alert, 'escalate')}>
                Escalate
              </Button>
              <Button
                variant="ghost"
                onClick={() => onAction(alert, 'false-positive')}
              >
                Mark false positive
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default AlertDetailDialog;
