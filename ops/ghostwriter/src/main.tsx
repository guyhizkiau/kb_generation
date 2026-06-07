import React from 'react'
import ReactDOM from 'react-dom/client'
import { MantineProvider, createTheme } from '@mantine/core'
import { Notifications } from '@mantine/notifications'
import { ModalsProvider } from '@mantine/modals'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { App } from './App'
import '@mantine/core/styles.css'
import '@mantine/notifications/styles.css'

const theme = createTheme({
  primaryColor: 'teal',
  colors: {
    teal: [
      '#e6f9f7',
      '#c0f0ea',
      '#8ae4da',
      '#4fd6c6',
      '#1fc8b5',
      '#0aac9a',
      '#028a7a',
      '#02635a',
      '#023632',
      '#011f1d',
    ],
  },
  white: '#F8F8FA',
  fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  defaultRadius: 'sm',
  components: {
    Card: { defaultProps: { radius: 'md' } },
  },
})

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <MantineProvider theme={theme}>
        <Notifications />
        <ModalsProvider modalProps={{ zIndex: 1100 }}>
          <App />
        </ModalsProvider>
      </MantineProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)
