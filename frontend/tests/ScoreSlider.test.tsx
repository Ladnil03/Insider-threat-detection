import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { ScoreSlider } from '../src/components/ScoreSlider';

describe('ScoreSlider Component', () => {
  it('renders with initial risk score and tier label', () => {
    const handleChange = vi.fn();
    render(<ScoreSlider value={0.72} onChange={handleChange} />);

    expect(screen.getByText('0.72')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
  });

  it('triggers onChange when range input changes', () => {
    const handleChange = vi.fn();
    render(<ScoreSlider value={0.50} onChange={handleChange} />);

    const slider = screen.getByRole('slider', { name: /Calibrated Analyst Risk Score/i });
    fireEvent.change(slider, { target: { value: '0.85' } });

    expect(handleChange).toHaveBeenCalledWith(0.85);
  });

  it('updates value using preset buttons', () => {
    const handleChange = vi.fn();
    render(<ScoreSlider value={0.20} onChange={handleChange} />);

    const criticalPreset = screen.getByRole('button', { name: /Critical \(0.90\)/i });
    fireEvent.click(criticalPreset);

    expect(handleChange).toHaveBeenCalledWith(0.90);
  });
});
