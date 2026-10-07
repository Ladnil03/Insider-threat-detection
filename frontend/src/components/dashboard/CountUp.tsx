import React, { useEffect, useState } from 'react';

interface CountUpProps {
  value: number;
  decimals?: number;
  duration?: number;
  className?: string;
}

/**
 * Subtle count-up on load (Skiper UI style): animates when `value` changes,
 * never on unrelated re-renders. Respects prefers-reduced-motion.
 */
export const CountUp: React.FC<CountUpProps> = ({
  value,
  decimals = 2,
  duration = 700,
  className,
}) => {
  const prefersReduced =
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const [display, setDisplay] = useState<number>(prefersReduced ? value : 0);

  useEffect(() => {
    if (prefersReduced) {
      setDisplay(value);
      return;
    }
    let raf = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const p = Math.min((now - start) / duration, 1);
      setDisplay(value * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value, duration, prefersReduced]);

  return (
    <span className={className} data-testid="countup">
      {display.toFixed(decimals)}
    </span>
  );
};

export default CountUp;
