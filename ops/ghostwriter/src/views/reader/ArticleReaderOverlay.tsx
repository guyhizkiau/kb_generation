import { useState, useEffect } from 'react'
import {
  Box, Group, Text, Badge, Button, ScrollArea, Stack, Anchor, Title, Skeleton,
} from '@mantine/core'
import { IconArrowLeft } from '@tabler/icons-react'
import { notifications } from '@mantine/notifications'
import { modals } from '@mantine/modals'
import { useQueryClient } from '@tanstack/react-query'
import { useQueue, useFeedback, useTrigger, useMergeArticle, articlePreviewUrl } from '@/api/hooks'
import { githubPullUrl } from '@/api/github'
import { AnnotationCard } from '@/components/AnnotationCard'

const PHASE_COLORS: Record<string, string> = {
  PLANNED: 'gray', DRAFTING: 'blue', TESTING: 'yellow', REVISING: 'orange',
  FINALIZING: 'violet', PR_OPEN: 'cyan', MERGED: 'teal', DONE: 'green',
  BLOCKED: 'red', UNKNOWN: 'gray',
}

const MERGED_PHASES = new Set(['MERGED', 'DONE'])

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
  const mergeArticle = useMergeArticle()
  const [dismissed, setDismissed] = useState<Set<string>>(new Set())
  const [previewState, setPreviewState] = useState<PreviewState>('loading')

  const article = queueData?.clusters
    .flatMap((c) => c.articles)
    .find((a) => a.slug === slug)

  const activeAnnotations = (feedbackData?.annotations ?? []).filter(
    (a) => !dismissed.has(a.id),
  )

  useEffect(() => {
    setPreviewState('loading')
  }, [slug])

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

  function handleMerge() {
    if (!article?.pr_number) return
    const early = !['PR_OPEN', 'FINALIZING', 'MERGED', 'DONE'].includes(article.phase)
    modals.openConfirmModal({
      title: 'Approve and push this PR?',
      children: (
        <Text size="sm">
          Push{' '}
          <strong>
            <a href={githubPullUrl(article.pr_number)} target="_blank" rel="noreferrer">
              PR #{article.pr_number}
            </a>
          </strong>{' '}
          for <strong>{slug}</strong> into <code>main</code>?
          {early && (
            <>
              {' '}
              This article is still in <strong>{article.phase}</strong> — only push if you
              intend to accept the current draft as-is.
            </>
          )}
        </Text>
      ),
      labels: { confirm: 'Push PR', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () =>
        mergeArticle.mutate(
          { slug, pr_number: article.pr_number },
          {
            onSuccess: () => {
              notifications.show({
                title: 'Pushed',
                message: `PR #${article.pr_number} pushed for ${slug}`,
                color: 'green',
              })
              onClose()
            },
            onError: (e) =>
              notifications.show({ title: 'Push failed', message: e.message, color: 'red' }),
          },
        ),
    })
  }

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
          {
            slug,
            reason: 'feedback',
            issue: article?.feedback_issue ?? '',
          },
          {
            onSuccess: () =>
              notifications.show({
                title: 'Launched',
                message: `Revision started for ${slug}`,
                color: 'teal',
              }),
            onError: (e) =>
              notifications.show({ title: 'Error', message: e.message, color: 'red' }),
          },
        ),
    })
  }

  function renderPreviewPane() {
    return (
      <Box style={{ position: 'relative', width: '100%', height: '100%' }}>
        {previewState === 'loading' && (
          <Stack p="md" gap="sm" style={{ position: 'absolute', inset: 0, zIndex: 1, background: '#fff' }}>
            <Skeleton height={28} width="60%" />
            <Skeleton height={16} width="40%" />
            <Skeleton height={200} mt="md" />
            <Skeleton height={120} />
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
          <Button
            variant="subtle"
            leftSection={<IconArrowLeft size={16} />}
            onClick={onClose}
          >
            Back
          </Button>
          <Box>
            <Title order={4}>{article?.title ?? slug}</Title>
            <Text size="xs" c="dimmed">{slug}</Text>
          </Box>
          {article?.phase && (
            <Badge color={PHASE_COLORS[article.phase] ?? 'gray'} variant="light">
              {article.phase}
            </Badge>
          )}
        </Group>
        <Group gap="xs">
          {article?.pr_number && !MERGED_PHASES.has(article.phase) && (
            <>
              <Anchor size="xs" href={githubPullUrl(article.pr_number)} target="_blank">
                PR #{article.pr_number}
              </Anchor>
              <Button size="sm" color="green" onClick={handleMerge}>
                Approve & push
              </Button>
            </>
          )}
          {article?.feedback_issue && (
            <Anchor
              size="xs"
              href={`https://github.com/guyhizkiau/kb_generation/issues/${article.feedback_issue}`}
              target="_blank"
            >
              Issue #{article.feedback_issue}
            </Anchor>
          )}
          {activeAnnotations.length > 0 && (
            <Button size="sm" color="teal" onClick={handleAccept}>
              Accept all → revise
            </Button>
          )}
          <Button size="xs" variant="light" onClick={() => refetch()}>
            Refresh comments
          </Button>
        </Group>
      </Group>

      <Box style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <Box style={{ flex: 1, minWidth: 0 }}>
          {renderPreviewPane()}
        </Box>
        <Box
          w={320}
          style={{
            borderLeft: '1px solid rgba(0,0,0,0.06)',
            background: '#fff',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Text fw={600} px="md" py="sm" size="sm">
            Comments ({activeAnnotations.length})
          </Text>
          <ScrollArea flex={1} px="md" pb="md">
            {fbLoading ? (
              <Text c="dimmed" size="sm">Loading…</Text>
            ) : activeAnnotations.length === 0 ? (
              <Stack gap="xs">
                <Text c="dimmed" size="sm">
                  Select text or an image in the article to add a comment.
                </Text>
              </Stack>
            ) : (
              activeAnnotations.map((ann) => (
                <AnnotationCard
                  key={ann.id}
                  ann={ann}
                  onAccept={handleAccept}
                  onDismiss={() =>
                    setDismissed((prev) => new Set([...prev, ann.id]))
                  }
                />
              ))
            )}
          </ScrollArea>
        </Box>
      </Box>
    </Box>
  )
}
