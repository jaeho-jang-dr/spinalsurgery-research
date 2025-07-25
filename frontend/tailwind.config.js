/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // VS Code Dark Theme Colors
        'vscode': {
          'bg': '#1e1e1e',
          'bg-light': '#252526',
          'bg-lighter': '#2d2d30',
          'sidebar': '#252526',
          'activity': '#333333',
          'titlebar': '#3c3c3c',
          'editor': '#1e1e1e',
          'hover': '#2a2d2e',
          'selection': '#264f78',
          'border': '#464647',
          'text': '#cccccc',
          'text-dim': '#969696',
          'text-bright': '#ffffff',
          'blue': '#007acc',
          'blue-light': '#1a85ff',
          'green': '#16c60c',
          'yellow': '#ffd700',
          'orange': '#ce9178',
          'red': '#f44747',
          'purple': '#c586c0',
        }
      },
      fontFamily: {
        'mono': ['Consolas', 'Monaco', 'Courier New', 'monospace'],
        'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      animation: {
        'spin-slow': 'spin 2s linear infinite',
      }
    },
  },
  plugins: [],
}