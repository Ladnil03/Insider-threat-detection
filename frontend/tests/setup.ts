import '@testing-library/jest-dom';

// Polyfill ResizeObserver for jsdom environment (required by Recharts ResponsiveContainer)
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
