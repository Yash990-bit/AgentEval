export default {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/**/*.html'],
  theme: {
    extend: {
      colors: {
        'bg-base': '#121214',
        'bg-surface': '#1C1C1E',
        'bg-card': '#242428',
        'bg-card-hover': '#2E2E32',
        'gold-primary': '#D4AF37',
        'gold-secondary': '#FFD700',
        'gold-soft': '#F5D76E',
        'gold-dim': '#8B6914',
        'text-primary': '#FFFFFF',
        'text-secondary': '#B3B3B3',
        'text-muted': '#666666',
        'danger': '#FF4444',
        'success': '#00C896',
        'warning': '#FF9500',
        'info': '#4A9EFF',
      },
      fontFamily: {
        display: ['Cormorant Garamond', 'serif'],
        body: ['DM Sans', 'sans-serif'],
        code: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
