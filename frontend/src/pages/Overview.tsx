import React, { useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';
import { cn } from 'cn';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Separator } from '../components/ui/separator';
import { Skeleton } from '../components/ui/skeleton';
import { Progress } from '../components/ui/progress';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { AlertRow } from '../components/dashboard/AlertRow';
import {
  AlertAction,
  AlertDetailDialog,
} from '../components/dashboard/AlertDetailDialog';
import { CountUp } from '../components/dashboard/CountUp';
import {
  Alert,
  MODEL_DESCRIPTIONS,
  ModelName,
  SEVERITY_META,
  Severity,
  activityRows,
  incomingAlert,
  modelScores,
  placeholderAlerts,
  severityForScore,
} from '../lib/dashboardData';

const ACTION_TOASTS: Record<AlertAction, { fn: typeof toast.success; msg: string }> = {
  acknowledge: { fn: toast.success, msg: 'Alert acknowledged' },
  escalate: { fn: toast.warning, msg: 'Alert escalated to tier 2' },
  'false-positive': { fn: toast.info, msg: 'Alert marked as false positive' },
};

const TIER_ORDER: Severity[] = ['critical', 'high', 'medium', 'low'];

const ScoreBlock: React.FC<{ score: number }> = ({ score }) => {
  const meta = SEVERITY_META[severityForScore(score)];
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-baseline gap-2">
        <CountUp value={score} className="font-mono text-3xl font-semibold text-foreground" />
        <span className={cn('text-sm font-medium', meta.text)}>{meta.label}</span>
      </div>
      <Progress
        value={score * 100}
        className="risk-progress h-1.5"
        style={{ '--risk-color': meta.color } as React.CSSProperties}
      />
      <p className="text-xs text-muted-foreground">SAI score, 0 to 1</p>
    </div>
  );
};

export const Overview: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>(placeholderAlerts);
  const [selected, setSelected] = useState<Alert | null>(null);
  const [scoresLoading, setScoresLoading] = useState<boolean>(true);

  // Simulated async score fetch — exercises the skeleton state.
  useEffect(() => {
    const t = setTimeout(() => setScoresLoading(false), 600);
    return () => clearTimeout(t);
  }, []);

  // Simulated live alert arrival — one toast, prepended to the feed.
  useEffect(() => {
    const t = setTimeout(() => {
      setAlerts((prev) =>
        prev.some((a) => a.id === incomingAlert.id) ? prev : [incomingAlert, ...prev]
      );
      toast.warning('New critical alert', {
        description: `${incomingAlert.userId} — ${incomingAlert.headline}`,
      });
    }, 7000);
    return () => clearTimeout(t);
  }, []);

  const counts = useMemo(() => {
    const c: Record<Severity, number> = { low: 0, medium: 0, high: 0, critical: 0 };
    alerts.forEach((a) => (c[a.severity] += 1));
    return c;
  }, [alerts]);

  const meanScore = useMemo(
    () => (alerts.length ? alerts.reduce((s, a) => s + a.score, 0) / alerts.length : 0),
    [alerts]
  );

  const handleAction = (alert: Alert, action: AlertAction) => {
    setAlerts((prev) => prev.filter((a) => a.id !== alert.id));
    setSelected(null);
    ACTION_TOASTS[action].fn(ACTION_TOASTS[action].msg, {
      description: `${alert.id} — ${alert.userId}`,
    });
  };

  return (
    <div className="flex flex-col gap-4 animate-in fade-in-0 slide-in-from-bottom-2 duration-500">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Alert feed */}
        <section className="flex min-w-0 flex-col gap-3 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Alert feed</CardTitle>
              <CardDescription>
                {alerts.length} open {alerts.length === 1 ? 'alert' : 'alerts'}, newest first
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-2">
              {alerts.length === 0 ? (
                <div className="flex flex-col items-center gap-2 rounded-xl border border-border/60 bg-muted/30 py-10 text-center">
                  <span className="size-2 rounded-full bg-risk-low" />
                  <p className="text-sm text-foreground">
                    All clear — no flagged activity in this window.
                  </p>
                  <p className="text-xs text-muted-foreground">
                    New PRISM and AIRS findings will appear here as they are scored.
                  </p>
                </div>
              ) : (
                <div className="feed-reveal flex max-h-[540px] flex-col gap-2 overflow-y-auto pr-1">
                  {alerts.map((a) => (
                    <AlertRow key={a.id} alert={a} onOpen={setSelected} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </section>

        {/* Right rail */}
        <aside className="flex min-w-0 flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Risk summary</CardTitle>
              <CardDescription>Open alerts in this window</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <div className="flex items-baseline gap-2">
                <CountUp
                  value={alerts.length}
                  decimals={0}
                  className="font-mono text-3xl font-semibold text-foreground"
                />
                <span className="text-sm text-muted-foreground">open alerts</span>
              </div>
              <Separator />
              <ul className="flex flex-col gap-2">
                {TIER_ORDER.map((tier) => (
                  <li key={tier} className="flex items-center gap-2 text-sm">
                    <span
                      className={cn('size-1.5 rounded-full', SEVERITY_META[tier].dot)}
                    />
                    <span className="text-foreground/90">{SEVERITY_META[tier].label}</span>
                    <span className="ml-auto font-mono text-sm text-muted-foreground">
                      <CountUp value={counts[tier]} decimals={0} />
                    </span>
                  </li>
                ))}
              </ul>
              <Separator />
              <div className="flex items-baseline justify-between text-sm">
                <span className="text-muted-foreground">Mean SAI</span>
                <CountUp value={meanScore} className="font-mono text-foreground" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Model scores</CardTitle>
              <CardDescription>Latest blended scoring pass</CardDescription>
            </CardHeader>
            <CardContent>
              {scoresLoading ? (
                <div className="flex flex-col gap-3">
                  <Skeleton className="h-8 w-40" />
                  <Skeleton className="h-1.5 w-full" />
                  <Skeleton className="h-4 w-48" />
                </div>
              ) : (
                <Tabs defaultValue="ensemble">
                  <TabsList className="h-auto w-full justify-start gap-1 p-1">
                    {(Object.keys(modelScores) as ModelName[]).map((name) => (
                      <TabsTrigger key={name} value={name} className="px-3 py-1.5">
                        {name}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                  {(Object.keys(modelScores) as ModelName[]).map((name) => (
                    <TabsContent key={name} value={name} className="pt-4">
                      <ScoreBlock score={modelScores[name]} />
                      <p className="mt-3 text-xs text-muted-foreground">
                        {MODEL_DESCRIPTIONS[name]}
                      </p>
                    </TabsContent>
                  ))}
                </Tabs>
              )}
            </CardContent>
          </Card>
        </aside>
      </div>

      {/* User activity log */}
      <Card>
        <CardHeader>
          <CardTitle>Recent user activity</CardTitle>
          <CardDescription>Scored events across monitored users</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Activity</TableHead>
                <TableHead>Model</TableHead>
                <TableHead className="text-right">SAI score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {activityRows.map((row) => {
                const meta = SEVERITY_META[severityForScore(row.score)];
                return (
                  <TableRow key={`${row.time}-${row.user}`}>
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      {row.time}
                    </TableCell>
                    <TableCell className="font-mono text-xs">{row.user}</TableCell>
                    <TableCell className="text-sm">{row.activity}</TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      {row.model}
                    </TableCell>
                    <TableCell className={cn('text-right font-mono text-xs', meta.text)}>
                      {row.score.toFixed(2)}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <AlertDetailDialog
        alert={selected}
        onOpenChange={(open) => !open && setSelected(null)}
        onAction={handleAction}
      />
    </div>
  );
};

export default Overview;
