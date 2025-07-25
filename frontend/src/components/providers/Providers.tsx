'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#252526',
            color: '#cccccc',
            border: '1px solid #464647',
            fontSize: '13px',
          },
          success: {
            iconTheme: {
              primary: '#16c60c',
              secondary: '#252526',
            },
          },
          error: {
            iconTheme: {
              primary: '#f44747',
              secondary: '#252526',
            },
          },
        }}
      />
    </QueryClientProvider>
  )
}