import {
  Grid, Card, Text, Badge, Group, Stack, Progress, Table,
  Button, Code, ScrollArea, Title, Box, Anchor,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { useStatus, usePollNow, useRetry } from '@/api/hooks'
import { githubPullUrl } from '@/api/github'

function StatusBadge({ label, ok }: { label: string; ok: boolean }) {
  return (
    <Badge color={ok ? 'teal' : 'red'} variant="filled" size="lg">
      {label}
    </Badge>
  )
}

export function HealthView() {
  const { data, isLoading, error } = useStatus()
  const pollNow = usePollNow()
  const retry = useRetry()

  if (isLoading) return <Text c="dimmed" mt="xl" ta="center">Loading...</Text>
  if (error) return <Text c="red" mt="xl" ta="center">Error loading status</Text>
  if (!data) return null

  const d = data.daemon
  const uptimeSecs = d.started_at
    ? Math.floor((Date.now() - new Date(d.started_at).getTime()) / 1000)
    : 0
  const uptimeStr =
    uptimeSecs > 3600
      ? `${Math.floor(uptimeSecs / 3600)}h ${Math.floor((uptimeSecs % 3600) / 60)}m`
      : `${Math.floor(uptimeSecs / 60)}m ${uptimeSecs % 60}s`

  return (
    <Stack gap="md">
      <Group justify="space-between" align="flex-start">
        <Box>
          <Title order={3}>Daemon Health</Title>
          <Text size="sm" c="dimmed">
            PID {d.pid} · uptime {uptimeStr} · polling every {d.poll_interval}s
          </Text>
        </Box>
        <Group gap="xs">
          <StatusBadge label={data.current_task ? 'busy' : 'idle'} ok={!data.last_error} />
          <Button
            size="sm"
            onClick={() =>
              pollNow.mutate(undefined, {
                onSuccess: () =>
                  notifications.show({ title: 'Triggered', message: 'Poll started', color: 'teal' }),
              })
            }
            loading={pollNow.isPending}
          >
            Poll now
          </Button>
        </Group>
      </Group>

      {/* Counters */}
      <Grid>
        {Object.entries(data.counters).map(([k, v]) => (
          <Grid.Col key={k} span={{ base: 6, sm: 3 }}>
            <Card withBorder p="sm">
              <Text size="xl" fw={700}>{v}</Text>
              <Text size="xs" c="dimmed">{k.replace(/_/g, ' ')}</Text>
            </Card>
          </Grid.Col>
        ))}
      </Grid>

      {/* Current task */}
      {data.current_task && (
        <Card withBorder>
          <Text fw={600} mb="xs">Active task</Text>
          <Text size="sm">
            PR #{data.current_task.pr_number} · step: {data.current_task.step}
          </Text>
          <Progress mt="xs" value={50} color="teal" animated />
        </Card>
      )}

      {/* Last error */}
      {data.last_error && (
        <Card withBorder style={{ borderColor: 'var(--mantine-color-red-4)' }}>
          <Text c="red" fw={600}>Last error</Text>
          <Code block mt="xs">{data.last_error.message}</Code>
          <Text size="xs" c="dimmed" mt={4}>{data.last_error.at}</Text>
        </Card>
      )}

      {/* Open PRs */}
      <Card withBorder>
        <Text fw={600} mb="xs">Open PRs ({data.open_prs.length})</Text>
        {data.open_prs.length === 0 ? (
          <Text size="sm" c="dimmed">None</Text>
        ) : (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>PR</Table.Th>
                <Table.Th>Branch</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.open_prs.map((pr) => (
                <Table.Tr key={pr.number}>
                  <Table.Td>
                    <Anchor
                      href={githubPullUrl(pr.number)}
                      target="_blank"
                      rel="noopener noreferrer"
                      size="sm"
                    >
                      #{pr.number}
                    </Anchor>
                  </Table.Td>
                  <Table.Td>
                    <Anchor
                      href={githubPullUrl(pr.number)}
                      target="_blank"
                      rel="noopener noreferrer"
                      size="sm"
                    >
                      <Code>{pr.branch}</Code>
                    </Anchor>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Card>

      {/* Failed comments */}
      {data.failed_comments.length > 0 && (
        <Card withBorder>
          <Text fw={600} mb="xs" c="orange">
            Failed comments ({data.failed_comments.length})
          </Text>
          <Table striped>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>ID</Table.Th>
                <Table.Th>PR</Table.Th>
                <Table.Th>Failure</Table.Th>
                <Table.Th>Action</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.failed_comments.map((fc) => (
                <Table.Tr key={fc.comment_id}>
                  <Table.Td><Code>{fc.comment_id}</Code></Table.Td>
                  <Table.Td>#{fc.pr_number}</Table.Td>
                  <Table.Td>{fc.failure}</Table.Td>
                  <Table.Td>
                    <Button
                      size="xs"
                      variant="light"
                      color="orange"
                      onClick={() =>
                        retry.mutate(fc.comment_id, {
                          onSuccess: () =>
                            notifications.show({ message: 'Retry queued', color: 'teal' }),
                        })
                      }
                    >
                      Retry
                    </Button>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Card>
      )}

      {/* Live log */}
      <Card withBorder>
        <Text fw={600} mb="xs">Recent log</Text>
        <ScrollArea h={280}>
          <Code block style={{ fontSize: '11px', whiteSpace: 'pre-wrap' }}>
            {(data.recent_log ?? []).join('\n')}
          </Code>
        </ScrollArea>
      </Card>
    </Stack>
  )
}
