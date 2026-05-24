import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // GitHub-inspired dark theme
        background: {
          primary: '#0d1117',
          secondary: '#161b22',
          tertiary: '#21262d',
        },
        border: {
          DEFAULT: '#30363d',
          muted: '#21262d',
        },
        text: {
          primary: '#c9d1d9',
          secondary: '#8b949e',
          muted: '#6e7681',
        },
        accent: {
          DEFAULT: '#58a6ff',
          hover: '#79c0ff',
        },
        success: '#3fb950',
        warning: '#d29922',
        error: '#f85149',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Cascadia Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
export default config
