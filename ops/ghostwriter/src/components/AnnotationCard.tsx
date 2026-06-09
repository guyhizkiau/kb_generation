import { Card, Text, Group, Stack, Button, Box, Tooltip } from '@mantine/core'
import type { Annotation } from '@/api/hooks'

export interface AnnotationCardProps {
  ann: Annotation
  onAccept?: () => void
  onDismiss?: () => void
  disabled?: boolean
}

export function AnnotationCard({
  ann,
  onAccept,
  onDismiss,
  disabled = false,
}: AnnotationCardProps) {
  const comment = ann.body.map((b) => b.value).join(' ')
  const selector = ann.target?.selector
  const isText = selector?.type === 'TextQuoteSelector'
  const isImage = selector?.type === 'FragmentSelector'

  return (
    <Card withBorder mb="sm" p="sm">
      <Stack gap="xs">
        {isText && selector.exact && (
          <Box
            p="xs"
            style={{
              borderLeft: '3px solid var(--mantine-color-teal-4)',
              background: 'var(--mantine-color-gray-0)',
              borderRadius: 4,
            }}
          >
            <Text size="xs" c="dimmed" fs="italic">
              &ldquo;{selector.exact.slice(0, 200)}&rdquo;
            </Text>
          </Box>
        )}
        {isImage && (
          <Box
            p="xs"
            style={{
              borderLeft: '3px solid var(--mantine-color-violet-4)',
              background: 'var(--mantine-color-gray-0)',
              borderRadius: 4,
            }}
          >
            <Text size="xs" c="dimmed">Image region: {selector.value}</Text>
            {ann.target?.source && (
              <Text size="xs" c="dimmed">
                File: {ann.target.source.split('/').pop()}
              </Text>
            )}
          </Box>
        )}
        <Text size="sm">{comment}</Text>
        <Group justify="space-between">
          <Text size="xs" c="dimmed">
            {ann.creator?.name ?? 'anonymous'}
            {ann.created ? ` · ${new Date(ann.created).toLocaleDateString()}` : ''}
          </Text>
          {onAccept && onDismiss && (
            <Group gap="xs" justify="flex-end">
              <Button size="xs" variant="subtle" color="gray" onClick={onDismiss} disabled={disabled}>
                Dismiss
              </Button>
              <Tooltip
                label="Revision in progress"
                disabled={!disabled}
                withArrow
              >
                <Button
                  size="xs"
                  color="teal"
                  onClick={onAccept}
                  disabled={disabled}
                  title={disabled ? 'Revision in progress' : undefined}
                >
                  Accept → revise
                </Button>
              </Tooltip>
            </Group>
          )}
        </Group>
      </Stack>
    </Card>
  )
}
