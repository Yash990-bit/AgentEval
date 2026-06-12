import type { Config } from 'tailwindcss';
import plugin from 'tailwindcss/plugin';

const glassMorphism = plugin(function({ addUtilities }) {
  addUtilities({
    '.glass': {
      '@apply backdrop-blur-md bg-white/10 border border-white/20 rounded-xl': {},
    },
  });
});

export default <Config>{
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,tsx,jsx}',
    './app/**/*.{js,ts,tsx,jsx}',
    './components/**/*.{js,ts,tsx,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: 'hsl(210, 70%, 58%)', // cool blue
        accent: 'hsl(45, 90%, 55%)', // golden
      },
    },
  },
  plugins: [
    require('class-variance-authority'),
    require('tailwind-merge'),
    glassMorphism,
  ],
};
