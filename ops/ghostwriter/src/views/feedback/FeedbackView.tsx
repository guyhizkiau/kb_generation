import { useEffect, useRef, useState } from 'react'
import {
  Grid, Card, Text, Badge, Group, Stack, Button,
  Title, Box, NavLink, ScrollArea, Anchor, Alert,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { modals } from '@mantine/modals'
import { useQueue, useFeedback, useTrigger, useDismissAnnotation } from '@/api/hooks'
import { AnnotationCard } from '@/components/AnnotationCard'
import { useReader } from '@/context/ReaderContext'
import { useNavigation } from '@/context/NavigationContext'

const PHASE_COLORS: Record<string, string> = {
  MERGED: 'teal', DONE: 'green', PR_OPEN: 'cyan',
  REVISING: 'orange', FINALIZING: 'violet', BLOCKED: 'red',
}

export function FeedbackView() {
  const { data: queueData, isLoading: queueLoading } = useQueue()
  const trigger = useTrigger()
  const dismissAnnotation = useDismissAnnotation()
  const { openReader } = useReader()
  const { feedbackSlug: selectedSlug, setFeedbackSlug } = useNavigation()

  const { data: feedbackData, isLoading: fbLoading } = useFeedback(selectedSlug ?? '')

  // Bridge the polling gap: set true immediately on trigger success, clear once
  // the queue confirms claude_running has cycled back to false.
  const [justTriggered, setJustTriggered] = useState(false)
  const prevClaudeRunning = useRef(false)
  useEffect(() => {
    const current = queueData?.claude_running ?? false
    if (prevClaudeRunning.current && !current) {
      setJustTriggered(false)
    }
    prevClaudeRunning.current = current
  }, [queueData?.claude_running])

  const revisionInProgress = justTriggered || trigger.isPending || queueData?.claude_running === true

  const articlesWithFeedback =
    queueData?.clusters
      .flatMap((c) => c.articles)
      .filter((a) => a.feedback_issue || a.phase === 'REVISING' || a.publish_stale) ?? []

  const activeAnnotations = feedbackData?.annotations ?? []
  const activeArticle = queueData?.clusters
    .flatMap((c) => c.articles)
    .find((a) => a.slug === selectedSlug)

  function handleAccept() {
    if (!selectedSlug) return
    modals.openConfirmModal({
      title: 'Accept this feedback?',
      children: (
        <Text size="sm">
          This will launch the <strong>revise-from-feedback</strong> phase for{' '}
          <strong>{selectedSlug}</strong>
          {activeArticle?.feedback_issue
            ? ` using issue #${activeArticle.feedback_issue}`
            : ''}
          .
        </Text>
      ),
      labels: { confirm: 'Launch revision', cancel: 'Cancel' },
      confirmProps: { color: 'teal' },
      onConfirm: () =>
        trigger.mutate(
          {
            slug: selectedSlug,
            reason: 'feedback',
            issue: activeArticle?.feedback_issue ?? '',
          },
          {
            onSuccess: () => {
              setJustTriggered(true)
              notifications.show({
                title: 'Launched',
                message: `Revision started for ${selectedSlug}`,
                color: 'teal',
              })
            },
            onError: (e) =>
              notifications.show({ title: 'Error', message: e.message, color: 'red' }),
          },
        ),
    })
  }

  function openArticle(slug: string) {
    setFeedbackSlug(slug)
    openReader(slug)
  }

  if (queueLoading) return <Text c="dimmed" mt="xl" ta="center">Loading...</Text>

  return (
    <Stack gap="md">
      <Title order={3}>Feedback</Title>
      <Text size="sm" c="dimmed">
        Annotation inbox — click an article to open the reader with inline comments.
      </Text>

      <Grid>
        <Grid.Col span={{ base: 12, sm: 3 }}>
          <Card withBorder p="xs">
            <Text size="xs" fw={600} c="dimmed" mb="xs">ARTICLES</Text>
            {articlesWithFeedback.length === 0 && (
              <Text size="sm" c="dimmed">No open feedback</Text>
            )}
            {articlesWithFeedback.map((art) => (
              <NavLink
                key={art.slug}
                label={art.title}
                active={selectedSlug === art.slug}
                onClick={() => openArticle(art.slug)}
                variant="filled"
                mb={2}
                rightSection={
                  <Group gap={4}>
                    {art.publish_stale && (
                      <Badge color="orange" size="xs">STALE</Badge>
                    )}
                    {art.phase && (
                      <Badge color={PHASE_COLORS[art.phase] ?? 'gray'} size="xs">
                        {art.phase}
                      </Badge>
                    )}
                  </Group>
                }
              />
            ))}
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 9 }}>
          {!selectedSlug ? (
            <Text c="dimmed" mt="xl" ta="center">
              Select an article to review its feedback
            </Text>
          ) : fbLoading ? (
            <Text c="dimmed" mt="xl" ta="center">Loading annotations...</Text>
          ) : (
            <Card withBorder>
              <Group justify="space-between" mb="md">
                <Box>
                  <Text fw={600}>{activeArticle?.title ?? selectedSlug}</Text>
                  {activeArticle?.feedback_issue && (
                    <Anchor
                      size="xs"
                      href={`https://github.com/guyhizkiau/kb_generation/issues/${activeArticle.feedback_issue}`}
                      target="_blank"
                      c="dimmed"
                    >
                      Issue #{activeArticle.feedback_issue}
                    </Anchor>
                  )}
                </Box>
                <Group gap="xs">
                  <Button size="sm" variant="light" onClick={() => openReader(selectedSlug)}>
                    Open reader
                  </Button>
                  {activeArticle?.revision_cycle != null &&
                    activeArticle.revision_cycle > 0 && (
                      <Badge color="violet">
                        Revision cycle {activeArticle.revision_cycle}
                      </Badge>
                    )}
                  {activeAnnotations.length > 0 && (
                    <Button
                      size="sm"
                      color="teal"
                      onClick={handleAccept}
                      disabled={revisionInProgress}
                      title={revisionInProgress ? 'Revision in progress' : undefined}
                    >
                      Accept all → revise
                    </Button>
                  )}
                </Group>
              </Group>

              {revisionInProgress && (
                <Alert color="yellow" mb="sm" title="Revision in progress…">
                  Claude is currently processing a revision. Buttons are disabled until it finishes.
                </Alert>
              )}

              {activeAnnotations.length === 0 ? (
                <Text c="dimmed">
                  No annotations loaded. Open the reader to add inline comments.
                </Text>
              ) : (
                <ScrollArea h={500}>
                  {activeAnnotations.map((ann) => (
                    <AnnotationCard
                      key={ann.id}
                      ann={ann}
                      onAccept={handleAccept}
                      disabled={revisionInProgress}
                      onDismiss={() => {
                        if (!selectedSlug) return
                        dismissAnnotation.mutate(
                          { slug: selectedSlug, id: ann.id },
                          {
                            onError: (e) =>
                              notifications.show({
                                title: 'Could not dismiss',
                                message: e.message,
                                color: 'red',
                              }),
                          },
                        )
                      }}
                    />
                  ))}
                </ScrollArea>
              )}
            </Card>
          )}
        </Grid.Col>
      </Grid>
    </Stack>
  )
}
