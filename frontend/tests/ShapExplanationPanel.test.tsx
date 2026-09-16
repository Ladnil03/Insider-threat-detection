import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { ShapExplanationPanel } from '../src/components/ShapExplanationPanel';
import { FeatureAttribution } from '../src/types';

describe('ShapExplanationPanel Component', () => {
  const mockFeatures: FeatureAttribution[] = [
    {
      feature: 'Mass USB File Exfiltration',
      raw_key: 'file_copy_usb',
      attribution: 0.284,
      value: 15,
      percentage: 42.5,
      direction: 'increased',
    },
    {
      feature: 'Standard Business Hours Logon',
      raw_key: 'logon_count',
      attribution: -0.092,
      value: 1,
      percentage: 13.8,
      direction: 'decreased',
    },
  ];

  it('renders loading state when isLoading is true', () => {
    render(<ShapExplanationPanel features={[]} isLoading={true} />);
    expect(screen.getByText(/Computing game-theoretic SHAP attributions/i)).toBeInTheDocument();
  });

  it('renders empty message when no features provided', () => {
    render(<ShapExplanationPanel features={[]} />);
    expect(screen.getByText(/Select an activity event from the timeline/i)).toBeInTheDocument();
  });

  it('renders feature items, base values, and summary text', () => {
    render(
      <ShapExplanationPanel
        features={mockFeatures}
        baseValue={0.052}
        saiScore={0.781}
        reconstructionError={0.142}
        summary="High volume USB file transfers drive 42.5% of total positive anomaly lift."
        topRiskDrivers={[
          { feature: 'Mass USB File Exfiltration', impact: 'CRITICAL', percentage: 42.5 },
        ]}
      />
    );

    expect(screen.getByText(/SHAP Anomaly Explainability/i)).toBeInTheDocument();
    expect(screen.getByText('0.0520')).toBeInTheDocument();
    expect(screen.getByText('0.7810')).toBeInTheDocument();
    expect(screen.getByText(/High volume USB file transfers/i)).toBeInTheDocument();
    expect(screen.getByText(/Mass USB File Exfiltration/i)).toBeInTheDocument();
  });
});
