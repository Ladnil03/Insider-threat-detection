import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { Overview } from '../src/pages/Overview';
import { TooltipProvider } from '../src/components/ui/tooltip';

const renderOverview = () =>
  render(
    <MemoryRouter>
      <TooltipProvider>
        <Overview />
      </TooltipProvider>
    </MemoryRouter>
  );

describe('Overview Page Component', () => {
  it('renders the alert feed with score badges and severity tiers', () => {
    renderOverview();

    expect(screen.getByText('Alert feed')).toBeInTheDocument();
    expect(screen.getAllByText('0.94').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Critical').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('u-1187').length).toBeGreaterThanOrEqual(1);
    expect(
      screen.getByText('After-hours USB mass copy to unmanaged drive')
    ).toBeInTheDocument();
    expect(screen.getByText('Recent user activity')).toBeInTheDocument();
  });

  it('opens the alert detail dialog with SHAP features and action row', () => {
    renderOverview();

    fireEvent.click(screen.getByLabelText('Open alert ALT-2026-0418'));

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(
      screen.getByText('After-hours USB activity 3.2σ above baseline')
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Acknowledge' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Escalate' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Mark false positive' })).toBeInTheDocument();
  });

  it('removes the alert from the feed when acknowledged', async () => {
    renderOverview();

    fireEvent.click(screen.getByLabelText('Open alert ALT-2026-0418'));
    fireEvent.click(screen.getByRole('button', { name: 'Acknowledge' }));

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      expect(screen.queryByLabelText('Open alert ALT-2026-0418')).not.toBeInTheDocument();
    });
  });
});
