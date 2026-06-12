import { Stack, Text, Title } from '@mantine/core'
import { PhaseBadge } from '@/components/PhaseBadge'
import { ResearchPanel } from '@/views/reader/ResearchPanel'

export interface InProgressPanelProps {
  slug: string
  phase: string
}

export function InProgressPanel({ slug, phase }: InProgressPanelProps) {
  const heading = phase === 'RESEARCHING' ? 'Research in progress' : 'Drafting in progress'

  return (
    <Stack p="md" gap="md">
      <PhaseBadge phase={phase} />
      <Title order={4}>{heading}</Title>
      <Text size="sm" c="dimmed">
        Preview will appear when a draft is ready. Research collected so far:
      </Text>
      <ResearchPanel slug={slug} />
    </Stack>
  )
}
