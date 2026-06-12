import { useState } from 'react'
import {
  Box, Title, Text, Stack, Card, Badge, Group, UnstyledButton,
} from '@mantine/core'
import { useDocs } from '@/api/hooks'
import { DocReaderOverlay } from '@/views/knowledge/DocReaderOverlay'

const GROUP_ORDER = ['Editorial', 'Canon', 'Product'] as const

export function KnowledgeView() {
  const { data, isLoading, isError } = useDocs()
  const [openDocId, setOpenDocId] = useState<string | null>(null)

  if (isLoading) {
    return (
      <Box p="lg">
        <Title order={2}>Knowledge</Title>
        <Text c="dimmed" mt="sm">Loading…</Text>
      </Box>
    )
  }

  if (isError) {
    return (
      <Box p="lg">
        <Title order={2}>Knowledge</Title>
        <Text c="red" mt="sm">Failed to load docs</Text>
      </Box>
    )
  }

  const docs = data?.docs ?? []

  return (
    <Box p="lg">
      <Title order={2} mb="md">Knowledge</Title>
      <Stack gap="xl">
        {GROUP_ORDER.map((group) => {
          const groupDocs = docs.filter((d) => d.group === group)
          if (groupDocs.length === 0) return null
          return (
            <Stack key={group} gap="sm">
              <Text fw={600} size="sm" c="dimmed">{group.toUpperCase()}</Text>
              {groupDocs.map((doc) => (
                <Card key={doc.id} padding="md" radius="md" withBorder>
                  {doc.exists ? (
                    <UnstyledButton
                      onClick={() => setOpenDocId(doc.id)}
                      style={{ width: '100%', textAlign: 'left' }}
                    >
                      <Group justify="space-between" wrap="nowrap">
                        <Box>
                          <Text fw={600}>{doc.title}</Text>
                          <Text size="xs" c="dimmed">{doc.path}</Text>
                          {doc.mtime != null && (
                            <Text size="xs" c="dimmed" mt={4}>
                              Updated {new Date(doc.mtime * 1000).toLocaleString()}
                            </Text>
                          )}
                        </Box>
                      </Group>
                    </UnstyledButton>
                  ) : (
                    <Group justify="space-between" wrap="nowrap">
                      <Box>
                        <Text fw={600}>{doc.title}</Text>
                        <Text size="xs" c="dimmed">{doc.path}</Text>
                      </Box>
                      <Badge color="gray" variant="light">not created yet</Badge>
                    </Group>
                  )}
                </Card>
              ))}
            </Stack>
          )
        })}
      </Stack>

      {openDocId && (
        <DocReaderOverlay docId={openDocId} onClose={() => setOpenDocId(null)} />
      )}
    </Box>
  )
}
