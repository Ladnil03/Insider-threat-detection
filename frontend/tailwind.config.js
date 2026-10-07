/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // OpenIRM spec tokens (shadcn semantic names)
        background: '#0B0F19',
        foreground: '#E6E9EF',
        card: { DEFAULT: '#161B22', foreground: '#E6E9EF' },
        popover: { DEFAULT: '#161B22', foreground: '#E6E9EF' },
        primary: { DEFAULT: '#6366F1', foreground: '#FFFFFF' },
        secondary: { DEFAULT: '#161B22', foreground: '#E6E9EF' },
        muted: { DEFAULT: '#161B22', foreground: '#8B92A5' },
        accent: { DEFAULT: '#161B22', foreground: '#E6E9EF' },
        destructive: { DEFAULT: '#EF4444', foreground: '#FFFFFF' },
        border: '#2D3344',
        input: '#2D3344',
        ring: '#6366F1',
        risk: {
          low: '#22C55E',
          medium: '#F59E0B',
          high: '#EF4444',
          critical: '#B91C1C',
        },
        // Legacy token names kept for existing pages, remapped to the new palette
        surface: '#0B0F19',
        'surface-container-lowest': '#0B0F19',
        'surface-container-low': '#111620',
        'surface-container': '#161B22',
        'surface-container-high': '#1C2230',
        'surface-container-highest': '#232A3A',
        'on-surface': '#E6E9EF',
        'on-surface-variant': '#8B92A5',
        'outline-variant': '#2D3344',
        tertiary: {
          DEFAULT: '#6366F1',
          dim: '#4F46E5',
          fixed: '#818CF8',
        },
        error: {
          DEFAULT: '#EF4444',
          dim: '#DC2626',
          container: '#B91C1C',
        },
        brand: {
          dark: '#0B0F19',
          card: '#161B22',
          accent: '#6366F1',
        },
      },
      fontFamily: {
        // Spec: two typefaces app-wide — Inter for UI, JetBrains Mono for numerics
        heading: ['Inter', 'sans-serif'],
        headline: ['Inter', 'sans-serif'],
        display: ['Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        label: ['Inter', 'sans-serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'glow-primary': '0 0 15px rgba(99, 102, 241, 0.25)',
        'glow-danger': '0 0 15px rgba(239, 68, 68, 0.25)',
        'glow-tertiary': '0 0 15px rgba(99, 102, 241, 0.25)',
      },
    },
  },
  plugins: [],
}
