import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { PolicyFeed } from '../src/pages/PolicyFeed';
import * as policyApi from '../src/api/policy';

vi.mock('../src/api/policy');

describe('PolicyFeed Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockViolations = [
    {
      id: 1,
      user_id: 'ACM2278',
      rule_id: 'RULE-USB-EXFIL',
      rule_name: 'Mass USB File Copy Exfiltration',
      severity: 'CRITICAL',
      action: 'REVOKE_USB_ACCESS',
      description: 'Copied 120 confidential files to unapproved drive.',
      timestamp: '2026-08-31T09:00:00Z',
    },
    {
      id: 2,
      user_id: 'CDE0012',
      rule_id: 'RULE-AFTER-HOURS-SPIKE',
      rule_name: 'Anomalous Off-Hours Logon Surge',
      severity: 'HIGH',
      action: 'NOTIFY_SOC_ANALYST',
      description: 'Logon occurred at 03:15 AM on weekend.',
      timestamp: '2026-08-31T08:30:00Z',
    },
  ];

  it('renders violation list from API', async () => {
    vi.mocked(policyApi.getPolicyViolations).mockResolvedValue(mockViolations);

    render(
      <MemoryRouter>
        <PolicyFeed />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Automated Policy Containment Feed/i)).toBeInTheDocument();
      expect(screen.getByText('Mass USB File Copy Exfiltration')).toBeInTheDocument();
      expect(screen.getByText('Anomalous Off-Hours Logon Surge')).toBeInTheDocument();
      expect(screen.getByText('ACM2278')).toBeInTheDocument();
      expect(screen.getByText('CDE0012')).toBeInTheDocument();
    });
  });

  it('filters violations by severity tab', async () => {
    vi.mocked(policyApi.getPolicyViolations).mockResolvedValue(mockViolations);

    render(
      <MemoryRouter>
        <PolicyFeed />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Mass USB File Copy Exfiltration')).toBeInTheDocument();
    });

    // Click CRITICAL filter tab
    const criticalTab = screen.getByRole('button', { name: 'CRITICAL' });
    fireEvent.click(criticalTab);

    // CRITICAL rule remains, HIGH rule disappears
    expect(screen.getByText('Mass USB File Copy Exfiltration')).toBeInTheDocument();
    expect(screen.queryByText('Anomalous Off-Hours Logon Surge')).not.toBeInTheDocument();
  });
});
