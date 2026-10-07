/**
 * Placeholder dashboard data. Fixtures live here until the feed is wired to
 * the scoring API (per plan: API wiring comes later on request).
 */

export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type ModelName = 'PRISM' | 'AIRS' | 'Ensemble';

export interface ShapFeature {
  label: string;
  sigma: number;
  attribution: number;
}

export interface Alert {
  id: string;
  time: string;
  userId: string;
  score: number;
  severity: Severity;
  models: ModelName[];
  headline: string;
  shap: ShapFeature[];
}

export const severityForScore = (score: number): Severity =>
  score >= 0.85 ? 'critical' : score >= 0.6 ? 'high' : score >= 0.3 ? 'medium' : 'low';

export const SEVERITY_META: Record<
  Severity,
  { label: string; text: string; border: string; dot: string; color: string }
> = {
  low: {
    label: 'Low',
    text: 'text-risk-low',
    border: 'border-l-risk-low',
    dot: 'bg-risk-low',
    color: '#22C55E',
  },
  medium: {
    label: 'Medium',
    text: 'text-risk-medium',
    border: 'border-l-risk-medium',
    dot: 'bg-risk-medium',
    color: '#F59E0B',
  },
  high: {
    label: 'High',
    text: 'text-risk-high',
    border: 'border-l-risk-high',
    dot: 'bg-risk-high',
    color: '#EF4444',
  },
  critical: {
    label: 'Critical',
    // #B91C1C fails contrast as text on the dark bg — text borrows risk-high,
    // the critical color stays on borders/dots/glow where it reads fine.
    text: 'text-risk-high',
    border: 'border-l-risk-critical',
    dot: 'bg-risk-critical',
    color: '#B91C1C',
  },
};

const rawAlerts: Omit<Alert, 'severity'>[] = [
  {
    id: 'ALT-2026-0418',
    time: 'Oct 07, 14:02:31',
    userId: 'u-1187',
    score: 0.94,
    models: ['PRISM', 'Ensemble'],
    headline: 'After-hours USB mass copy to unmanaged drive',
    shap: [
      {
        label: 'After-hours USB activity 3.2σ above baseline',
        sigma: 3.2,
        attribution: 0.21,
      },
      { label: 'External drive first seen 4 days ago', sigma: 2.1, attribution: 0.14 },
      { label: 'Copy volume 18× the user’s weekly norm', sigma: 2.8, attribution: 0.17 },
    ],
  },
  {
    id: 'ALT-2026-0417',
    time: 'Oct 07, 13:47:09',
    userId: 'u-2041',
    score: 0.87,
    models: ['AIRS', 'Ensemble'],
    headline: 'VPN login from a new country outside working hours',
    shap: [
      {
        label: 'Geo-velocity anomaly 2.9σ above baseline',
        sigma: 2.9,
        attribution: 0.19,
      },
      { label: 'Login at 02:14 local time', sigma: 2.4, attribution: 0.12 },
      { label: 'New device fingerprint for this account', sigma: 1.9, attribution: 0.09 },
    ],
  },
  {
    id: 'ALT-2026-0416',
    time: 'Oct 07, 13:12:55',
    userId: 'u-3320',
    score: 0.78,
    models: ['AIRS', 'PRISM', 'Ensemble'],
    headline: 'Bulk export of customer records to personal cloud storage',
    shap: [
      {
        label: 'Database export 4.1σ above baseline',
        sigma: 4.1,
        attribution: 0.24,
      },
      { label: 'Destination domain not on the allow list', sigma: 2.2, attribution: 0.11 },
      { label: 'Export skipped the usual reporting job', sigma: 1.7, attribution: 0.07 },
    ],
  },
  {
    id: 'ALT-2026-0415',
    time: 'Oct 07, 12:41:18',
    userId: 'u-0912',
    score: 0.58,
    models: ['PRISM'],
    headline: 'Shared credential used from two locations in one hour',
    shap: [
      {
        label: 'Concurrent sessions from two geographies',
        sigma: 2.0,
        attribution: 0.13,
      },
      { label: 'Service account used interactively', sigma: 1.6, attribution: 0.08 },
      { label: 'No MFA challenge recorded', sigma: 1.4, attribution: 0.06 },
    ],
  },
  {
    id: 'ALT-2026-0414',
    time: 'Oct 07, 11:58:02',
    userId: 'u-5503',
    score: 0.47,
    models: ['AIRS'],
    headline: 'Unusual volume of failed access attempts to the finance share',
    shap: [
      {
        label: 'Failed access rate 2.3σ above baseline',
        sigma: 2.3,
        attribution: 0.12,
      },
      { label: 'Accessing a team the user never works with', sigma: 1.8, attribution: 0.07 },
      { label: 'Attempts clustered within a 90-second window', sigma: 1.5, attribution: 0.05 },
    ],
  },
  {
    id: 'ALT-2026-0413',
    time: 'Oct 07, 10:33:44',
    userId: 'u-7724',
    score: 0.24,
    models: ['PRISM'],
    headline: 'Minor policy deviation: document downloaded twice',
    shap: [
      { label: 'Repeat download 1.1σ above baseline', sigma: 1.1, attribution: 0.05 },
      { label: 'Known trusted device', sigma: -1.2, attribution: -0.04 },
      { label: 'Normal hours for this user', sigma: -0.9, attribution: -0.03 },
    ],
  },
];

export const placeholderAlerts: Alert[] = rawAlerts.map((a) => ({
  ...a,
  severity: severityForScore(a.score),
}));

/** Alert that "arrives" a few seconds after load, to demo the live toast. */
export const incomingAlert: Alert = {
  id: 'ALT-2026-0419',
  time: 'Oct 07, 14:09:03',
  userId: 'u-4410',
  score: 0.91,
  severity: 'critical',
  models: ['PRISM', 'AIRS', 'Ensemble'],
  headline: 'Customer records bulk download outside change window',
  shap: [
    { label: 'Record count 5.6σ above baseline', sigma: 5.6, attribution: 0.28 },
    { label: 'No linked change or incident ticket', sigma: 2.6, attribution: 0.15 },
    { label: 'Destination is a personal email gateway', sigma: 2.4, attribution: 0.13 },
  ],
};

export const modelScores: Record<ModelName, number> = {
  PRISM: 0.45,
  AIRS: 0.83,
  Ensemble: 0.74,
};

export const MODEL_DESCRIPTIONS: Record<ModelName, string> = {
  PRISM: 'Rule-based checks from the policy engine',
  AIRS: 'Autoencoder reconstruction error on activity features',
  Ensemble: 'Blended SAI score across both models',
};

export interface ActivityRow {
  time: string;
  user: string;
  activity: string;
  model: ModelName;
  score: number;
}

export const activityRows: ActivityRow[] = [
  { time: '14:02:31', user: 'u-1187', activity: 'USB mass copy (2.4 GB)', model: 'PRISM', score: 0.94 },
  { time: '13:47:09', user: 'u-2041', activity: 'VPN login, new geo', model: 'AIRS', score: 0.87 },
  { time: '13:12:55', user: 'u-3320', activity: 'Customer DB export', model: 'Ensemble', score: 0.78 },
  { time: '12:41:18', user: 'u-0912', activity: 'Concurrent session overlap', model: 'PRISM', score: 0.58 },
  { time: '11:58:02', user: 'u-5503', activity: 'Failed access burst', model: 'AIRS', score: 0.47 },
];
