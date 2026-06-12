import { useState, useEffect, useRef } from 'react'
import {
  Box, Group, Text, Button, ScrollArea, Stack, Anchor, Title, Skeleton, Alert, Tabs,
} from '@mantine/core'
import { IconArrowLeft } from '@tabler/icons-react'
import { notifications } from '@mantine/notifications'
import { modals } from '@mantine/modals'
import { useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import {
  useQueue, useFeedback, useTrigger, useDismissAnnotation,
  usePreviewAvailable, useTestNotes, articlePreviewUrl,
} from '@/api/hooks'
import { AnnotationCard } from '@/components/AnnotationCard'
import { PhaseBadge } from '@/components/PhaseBadge'
import { ResearchPanel } from '@/views/reader/ResearchPanel'
import { InProgressPanel } from '@/views/reader/InProgressPanel'

type PreviewState = 'loading' | 'ready'

export interface ArticleReaderOverlayProps {
  slug: string
  onClose: () => void
}

export function ArticleReaderOverlay({ slug, onClose }: ArticleReaderOverlayProps) {
  const queryClient = useQueryClient()
  const { data: queueData } = useQueue()
  const { data: feedbackData, isLoading: fbLoading, refetch } = useFeedback(slug)
  const trigger = useTrigger()
  const dismissAnnotation = useDismissAnnotation()
  const [previewState, setPreviewState] = useState<PreviewState>('loading')
  const [activeTab, setActiveTab] = useState<string | null>(null)
  const [justTriggered, setJustTriggered] = useState(false)
  const prevClaudeRunning = useRef(false)

  const article = queueData?.clusters
    .flatMap((c) => c.articles)
    .find((a) => a.slug === slug)

  const phase = article?.phase ?? ''
  const { data: previewAvail } = usePreviewAvailable(slug, phase)
  const previewReady = previewAvail?.available === true

  const { data: testNotes, isError: testNotesError } = useTestNotes(
    slug,
    activeTab === 'test-notes',
  )

  useEffect(() => {
    const current = queueData?.claude_running ?? false
    if (prevClaudeRunning.current && !current) setJustTriggered(false)
    prevClaudeRunning.current = current
  }, [queueData?.claude_running])

  const revisionInProgress = justTriggered || trigger.isPending || queueData?.claude_running === true
  const activeAnnotations = feedbackData?.annotations ?? []

  useEffect(() => {
    setPreviewState('loading')
  }, [slug])

  useEffect(() => {
    if (previewAvail === undefined) return
    setActiveTab((prev) => {
      if (prev !== null) return prev
      return previewReady ? 'preview' : 'research'
    })
  }, [previewAvail, previewReady])

  useEffect(() => {
    if (previewReady && activeTab === 'research' && previewAvail !== undefined) {
      setActiveTab('preview')
    }
  }, [previewReady, previewAvail, activeTab])

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const data = event.data as { type?: string; slug?: string } | null
      if (data?.type === 'ghostwriter:annotation-created' && data.slug === slug) {
        refetch()
        queryClient.invalidateQueries({ queryKey: ['feedback', slug] })
      }
    }
    window.addEventListener('message', onMessage)
    return () => window.removeEventListener('message', onMessage)
  }, [slug, refetch, queryClient])

  function handleAccept() {
    modals.openConfirmModal({
      title: 'Accept this feedback?',
      children: (
        <Text size="sm">
          Launch <strong>revise-from-feedback</strong> for <strong>{slug}</strong>?
        </Text>
      ),
      labels: { confirm: 'Launch revision', cancel: 'Cancel' },
      confirmProps: { color: 'teal' },
      onConfirm: () =>
        trigger.mutate(
          { slug, reason: 'feedback', issue: article?.feedback_issue ?? '' },
          {
            onSuccess: () => {
              setJustTriggered(true)
              notifications.show({
                title: 'Launched',
                message: `Revision started for ${slug}`,
                color: 'teal',
              })
            },
            onError: (e) =>
              notifications.show({ title: 'Error', message: e.message, color: 'red' }),
          },
        ),
    })
  }

  function renderPreviewContent() {
    if (!previewReady) {
      return <InProgressPanel slug={slug} phase={phase || 'DRAFTING'} />
    }
    return (
      <Box style={{ position: 'relative', width: '100%', height: '100%' }}>
        {previewState === 'loading' && (
          <Stack p="md" gap="sm" style={{ position: 'absolute', inset: 0, zIndex: 1, background: '#fff' }}>
            <Skeleton height={28} width="60%" />
            <Skeleton height={200} />
          </Stack>
        )}
        <iframe
          title={`Preview: ${slug}`}
          src={articlePreviewUrl(slug)}
          onLoad={() => setPreviewState('ready')}
          style={{ width: '100%', height: '100%', border: 'none', background: '#fff' }}
        />
      </Box>
    )
  }

  const tabValue = activeTab ?? (previewReady ? 'preview' : 'research')

  return (
    <Box
      data-testid="article-reader-overlay"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 1000,
        background: '#F8F8FA',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Group
        px="md"
        py="sm"
        justify="space-between"
        style={{ background: '#fff', borderBottom: '1px solid rgba(0,0,0,0.06)' }}
      >
        <Group gap="sm">
          <Button variant="subtle" leftSection={<IconArrowLeft size={16} />} onClick={onClose}>
            Back
          </Button>
          <Box>
            <Title order={4}>{article?.title ?? slug}</Title>
            <Text size="xs" c="dimmed">{slug}</Text>
          </Box>
          {article?.phase && (
            <PhaseBadge
              phase={article.phase}
              lastUpdate={article.last_update}
              running={queueData?.claude_running}
            />
          )}
        </Group>
        <Group gap="xs">
          {article?.feedback_issue && (
            <Anchor
              size="xs"
              href={`https://github.com/guyhizkiau/kb_generation/issues/${article.feedback_issue}`}
              target="_blank"
            >
              Issue #{article.feedback_issue}
            </Anchor>
          )}
          {activeTab === 'preview' && previewReady && activeAnnotations.length > 0 && (
            <Button size="sm" color="teal" disabled={revisionInProgress} onClick={handleAccept}>
              Accept feedback
            </Button>
          )}
        </Group>
      </Group>

      <Box style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <Box style={{ flex: 3, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
          <Tabs
            value={tabValue}
            onChange={(v) => setActiveTab(v ?? 'preview')}
            style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}
          >
            <Tabs.List px="md">
              <Tabs.Tab value="preview">Preview</Tabs.Tab>
              <Tabs.Tab value="research">Research</Tabs.Tab>
              <Tabs.Tab value="test-notes">Test notes</Tabs.Tab>
            </Tabs.List>
            <Tabs.Panel value="preview" style={{ flex: 1, minHeight: 0 }}>
              {renderPreviewContent()}
            </Tabs.Panel>
            <Tabs.Panel value="research" p="md" style={{ flex: 1, overflow: 'auto' }}>
              <ResearchPanel slug={slug} />
            </Tabs.Panel>
            <Tabs.Panel value="test-notes" p="md" style={{ flex: 1, overflow: 'auto' }}>
              {testNotesError && (
                <Text c="dimmed" size="sm">No test notes yet.</Text>
              )}
              {testNotes?.content && (
                <ReactMarkdown>{testNotes.content}</ReactMarkdown>
              )}
            </Tabs.Panel>
          </Tabs>
        </Box>

        {tabValue === 'preview' && previewReady && (
          <ScrollArea style={{ flex: 1, minWidth: 280, maxWidth: 360 }} p="md">
            <Text size="xs" fw={600} c="dimmed" mb="sm">
              ANNOTATIONS ({activeAnnotations.length})
            </Text>
            {fbLoading && <Text size="sm" c="dimmed">Loading…</Text>}
            {!fbLoading && activeAnnotations.length === 0 && (
              <Text size="sm" c="dimmed">No annotations yet. Select text in the preview to add one.</Text>
            )}
            <Stack gap="sm">
              {activeAnnotations.map((ann) => (
                <AnnotationCard
                  key={ann.id}
                  ann={ann}
                  onAccept={handleAccept}
                  disabled={revisionInProgress}
                  onDismiss={() =>
                    dismissAnnotation.mutate(
                      { slug, id: ann.id },
                      {
                        onError: (e) =>
                          notifications.show({ title: 'Dismiss failed', message: e.message, color: 'red' }),
                      },
                    )
                  }
                />
              ))}
            </Stack>
            {revisionInProgress && (
              <Alert color="teal" mt="md" title="Revision in progress">
                Claude is revising this article from your feedback.
              </Alert>
            )}
          </ScrollArea>
        )}
      </Box>
    </Box>
  )
}
