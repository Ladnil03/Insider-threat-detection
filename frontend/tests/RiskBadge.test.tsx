import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { RiskBadge } from '../src/components/RiskBadge';

describe('RiskBadge Component', () => {
  it('renders LOW risk level with correct text', () => {
    render(<RiskBadge level="LOW" />);
    const badge = screen.getByTestId('risk-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent('LOW');
  });

  it('renders MODERATE risk level when passed MODERATE or MEDIUM', () => {
    const { rerender } = render(<RiskBadge level="MODERATE" />);
    expect(screen.getByTestId('risk-badge')).toHaveTextContent('MODERATE');

    rerender(<RiskBadge level="MEDIUM" />);
    expect(screen.getByTestId('risk-badge')).toHaveTextContent('MODERATE');
  });

  it('renders HIGH risk level', () => {
    render(<RiskBadge level="HIGH" />);
    const badge = screen.getByTestId('risk-badge');
    expect(badge).toHaveTextContent('HIGH');
  });

  it('renders CRITICAL risk level', () => {
    render(<RiskBadge level="CRITICAL" />);
    const badge = screen.getByTestId('risk-badge');
    expect(badge).toHaveTextContent('CRITICAL');
  });

  it('displays numerical score when showScore is true', () => {
    render(<RiskBadge level="HIGH" score={0.7892} showScore={true} />);
    const badge = screen.getByTestId('risk-badge');
    expect(badge).toHaveTextContent('(0.789)');
  });
});
