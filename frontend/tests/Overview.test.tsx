import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { Overview } from '../src/pages/Overview';
import * as scoringApi from '../src/api/scoring';
import * as policyApi from '../src/api/policy';

vi.mock('../src/api/scoring');
vi.mock('../src/api/policy');

describe('Overview Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially while aggregating telemetry', () => {
    vi.mocked(scoringApi.getMonitoredUsers).mockReturnValue(new Promise(() => {}));
    vi.mocked(policyApi.getPolicyViolations).mockReturnValue(new Promise(() => {}));

    render(
      <MemoryRouter>
        <Overview />
      </MemoryRouter>
    );

    expect(
      screen.getByText(/Aggregating real-time telemetry from PRISM & AIRS engines/i)
    ).toBeInTheDocument();
  });

  it('renders error state with retry button when API fails', async () => {
    vi.mocked(scoringApi.getMonitoredUsers).mockRejectedValue(
      new Error('Connection refused from FastAPI server.')
    );
    vi.mocked(policyApi.getPolicyViolations).mockResolvedValue([]);

    render(
      <MemoryRouter>
        <Overview />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to Load Dashboard Data/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Connection refused from FastAPI server./i)
      ).toBeInTheDocument();
      expect(screen.getByText(/Retry Connection/i)).toBeInTheDocument();
    });
  });

  it('renders dashboard with stats and top risk user table when data loads', async () => {
    vi.mocked(scoringApi.getMonitoredUsers).mockResolvedValue([
      {
        user_id: 'ACM2278',
        user_name: 'Alice Smith',
        role: 'Senior Engineer',
        department: 'R&D',
        latest_score: 0.885,
        risk_level: 'CRITICAL',
        latest_activity_date: '2026-08-19',
        violation_count: 2,
      },
      {
        user_id: 'CDE0012',
        user_name: 'Bob Jones',
        role: 'Accountant',
        department: 'Finance',
        latest_score: 0.21,
        risk_level: 'LOW',
        latest_activity_date: '2026-08-19',
        violation_count: 0,
      },
    ]);

    vi.mocked(policyApi.getPolicyViolations).mockResolvedValue([
      {
        id: 1,
        user_id: 'ACM2278',
        rule_id: 'RULE-USB-EXFIL',
        rule_name: 'Mass USB File Copy Exfiltration',
        severity: 'CRITICAL',
        action: 'REVOKE_USB_ACCESS',
        description: 'Large external drive transfer detected.',
        timestamp: '2026-08-19T10:00:00Z',
      },
    ]);

    render(
      <MemoryRouter>
        <Overview />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/SOC Threat Operations/i)).toBeInTheDocument();
      expect(screen.getByText('Alice Smith')).toBeInTheDocument();
      expect(screen.getByText('ACM2278')).toBeInTheDocument();
      expect(screen.getByText('CRITICAL')).toBeInTheDocument();
      expect(screen.getByText('2 alerts')).toBeInTheDocument();
    });
  });
});
