import { ReactElement, ReactNode } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { MantineProvider } from '@mantine/core'
import { Notifications } from '@mantine/notifications'
import { ModalsProvider } from '@mantine/modals'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NavigationProvider } from '@/context/NavigationContext'

function Providers({ children }: { children: ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider>
        <Notifications />
        <ModalsProvider>
          <NavigationProvider>{children}</NavigationProvider>
        </ModalsProvider>
      </MantineProvider>
    </QueryClientProvider>
  )
}

export function renderWithProviders(ui: ReactElement, options?: RenderOptions) {
  return render(ui, { wrapper: Providers, ...options })
}
