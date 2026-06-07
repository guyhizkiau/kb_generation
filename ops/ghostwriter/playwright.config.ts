import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/browser',
  outputDir: './test-results',
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: 'http://localhost:4173/ghostwriter/',
    trace: 'off',
    screenshot: 'on',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'npm run build && npm run preview -- --port 4173 --strictPort',
    url: 'http://localhost:4173/ghostwriter/',
    reuseExistingServer: false,
    timeout: 120_000,
  },
})
