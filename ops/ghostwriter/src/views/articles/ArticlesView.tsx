import { useState, useCallback } from 'react'
import {
  Grid, Card, Text, Badge, Group, Stack, Button, Select,
  Switch, ActionIcon, Title, Box, NavLink, TextInput,
  SegmentedControl, Tooltip, UnstyledButton, Textarea, Collapse,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { modals } from '@mantine/modals'
import { useQueries } from '@tanstack/react-query'
import {
  DndContext, closestCenter, KeyboardSensor, PointerSensor,
  useSensor, useSensors,
} from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import {
  arrayMove, SortableContext, sortableKeyboardCoordinates,
  verticalListSortingStrategy, useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
  useQueue, useSaveQueue, useTrigger, useApproveArticle,
  useRequestChanges, useDeleteArticle, useResolveBlocked, useTestNotes,
} from '@/api/hooks'
import { apiFetch } from '@/api/client'
import type { QueueData, ArticleEntry, Cluster } from '@/api/hooks'
import { partitionArticles } from '@/lib/articlePhase'
import { ConfirmDeleteModal } from '@/components/ConfirmDeleteModal'
import { DeleteArticleModal } from '@/components/DeleteArticleModal'
import { PhaseBadge } from '@/components/PhaseBadge'
import { useReader } from '@/context/ReaderContext'
import { useNavigation } from '@/context/NavigationContext'

/** Strip API-enriched fields before PUT /api/queue. */
export function toPersistableQueue(q: QueueData): Pick<QueueData, 'version' | 'clusters'> {
  return {
    version: q.version,
    clusters: q.clusters.map((c) => ({
      id: c.id,
      title: c.title,
      mode: c.mode,
      status: c.status,
      pause_after: c.pause_after,
      articles: c.articles.map((a) => ({ slug: a.slug, title: a.title })),
    })) as Cluster[],
  }
}

function canApproveArticle(art: ArticleEntry): boolean {
  return art.phase === 'IN_REVIEW'
}

function BlockedArticleRow({
  art,
  onDelete,
}: {
  art: ArticleEntry
  onDelete: () => void
}) {
  const [instructions, setInstructions] = useState('')
  const [showNotes, setShowNotes] = useState(false)
  const resolveBlocked = useResolveBlocked()
  const { data: testNotes } = useTestNotes(art.slug, showNotes)

  return (
    <Box
      style={{
        padding: '12px 14px',
        borderRadius: 6,
        border: '1px solid var(--mantine-color-red-3)',
        background: 'var(--mantine-color-red-0)',
        marginBottom: 8,
      }}
    >
      <Group justify="space-between" wrap="nowrap" mb="xs">
        <Stack gap={2}>
          <Text size="sm" fw={600} c="red">{art.title}</Text>
          <Text size="xs" c="dimmed">{art.slug}</Text>
        </Stack>
        <Group gap={4}>
          <PhaseBadge phase={art.phase} lastUpdate={art.last_update} />
          <ActionIcon
            size="xs"
            color="red"
            variant="subtle"
            aria-label={`Delete ${art.slug}`}
            onClick={onDelete}
          >
            ✕
          </ActionIcon>
        </Group>
      </Group>
      <Text size="xs" fw={600} c="red" mb={4}>Pipeline blocked</Text>
      <Text
        size="xs"
        ff="monospace"
        mb="sm"
        style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
      >
        {art.blocked_reason || 'No reason recorded'}
      </Text>
      {art.resume_phase && (
        <Text size="xs" c="dimmed" mb="sm">Resume phase: {art.resume_phase}</Text>
      )}
      <Button
        size="xs"
        variant="subtle"
        color="gray"
        mb="sm"
        onClick={() => setShowNotes((v) => !v)}
      >
        {showNotes ? 'Hide test notes' : 'Show test notes'}
      </Button>
      <Collapse in={showNotes}>
        <Box
          mb="sm"
          p="xs"
          style={{
            maxHeight: 200,
            overflow: 'auto',
            background: 'var(--mantine-color-gray-0)',
            borderRadius: 4,
            fontFamily: 'monospace',
            fontSize: 11,
            whiteSpace: 'pre-wrap',
          }}
        >
          {testNotes?.content ?? 'Loading…'}
        </Box>
      </Collapse>
      <Textarea
        label="Instructions for fixing this"
        placeholder="e.g. Step 05 should click Share a folder, not Share files"
        minRows={3}
        value={instructions}
        onChange={(e) => setInstructions(e.currentTarget.value)}
        mb="sm"
      />
      <Button
        size="sm"
        color="red"
        loading={resolveBlocked.isPending}
        disabled={!instructions.trim()}
        onClick={() =>
          resolveBlocked.mutate(
            { slug: art.slug, instructions: instructions.trim() },
            {
              onSuccess: () => {
                setInstructions('')
                notifications.show({
                  title: 'Retry queued',
                  message: `${art.slug} unblocked with your instructions`,
                  color: 'teal',
                })
              },
              onError: (e) =>
                notifications.show({ title: 'Retry failed', message: e.message, color: 'red' }),
            },
          )
        }
      >
        Retry with instructions
      </Button>
    </Box>
  )
}

function ReviewArticleRow({
  art,
  commentCount,
  claudeRunning,
  isActive,
  onReview,
  onApprove,
  onRequestChanges,
  onDelete,
}: {
  art: ArticleEntry
  commentCount: number
  claudeRunning?: boolean
  isActive?: boolean
  onReview: () => void
  onApprove: () => void
  onRequestChanges: () => void
  onDelete: () => void
}) {
  return (
    <Box
      style={{
        padding: '8px 12px',
        borderRadius: 6,
        border: '1px solid var(--mantine-color-gray-2)',
        marginBottom: 6,
      }}
    >
      <Group justify="space-between" wrap="nowrap">
        <UnstyledButton
          onClick={onReview}
          aria-label={`Review ${art.title}`}
          styles={{
            root: {
              borderRadius: 4,
              padding: '2px 6px',
              margin: '-2px -6px',
              transition: 'background-color 100ms ease',
              '&:hover': {
                backgroundColor: 'var(--mantine-color-gray-1)',
              },
            },
          }}
        >
          <Stack gap={2} ta="left">
            <Text size="sm" fw={500}>{art.title}</Text>
            <Text size="xs" c="dimmed">{art.slug}</Text>
          </Stack>
        </UnstyledButton>
        <Group gap={4} wrap="nowrap">
          {commentCount > 0 && (
            <Badge color="gray" size="xs">{commentCount} comments</Badge>
          )}
          {art.publish_stale && <Badge color="orange" size="xs">STALE</Badge>}
          {art.rework_reason && <Badge color="red" size="xs">REWORK</Badge>}
          {art.revision_cycle > 0 && (
            <Badge color="violet" size="xs">cycle {art.revision_cycle}</Badge>
          )}
          <PhaseBadge
            phase={art.phase}
            lastUpdate={art.last_update}
            running={claudeRunning}
            forceActivity={isActive}
          />
          {canApproveArticle(art) && (
            <>
              <Button size="xs" color="green" variant="light" onClick={onApprove}>
                Approve
              </Button>
              <Button size="xs" color="orange" variant="light" onClick={onRequestChanges}>
                Request changes
              </Button>
            </>
          )}
          <Button size="xs" color="teal" variant="light" onClick={onReview}>
            Review
          </Button>
          <ActionIcon
            size="xs"
            color="red"
            variant="subtle"
            aria-label={`Delete ${art.slug}`}
            onClick={onDelete}
          >
            ✕
          </ActionIcon>
        </Group>
      </Group>
    </Box>
  )
}

function SortableArticleRow({
  art,
  isNext,
  claudeRunning,
  isActive,
  onRemove,
  onWriteNext,
}: {
  art: ArticleEntry
  isNext: boolean
  claudeRunning?: boolean
  isActive?: boolean
  onRemove: () => void
  onWriteNext: (slug: string) => void
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: art.slug })

  return (
    <Box
      ref={setNodeRef}
      style={{
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
        padding: '8px 12px',
        borderRadius: 6,
        background: isDragging ? 'var(--mantine-color-gray-1)' : 'transparent',
        border: isNext
          ? '2px solid var(--mantine-color-teal-4)'
          : '1px solid var(--mantine-color-gray-2)',
        marginBottom: 6,
      }}
    >
      <Group justify="space-between" wrap="nowrap">
        <Group gap="xs" wrap="nowrap" style={{ cursor: 'grab' }} {...attributes} {...listeners}>
          <Text size="xs" c="dimmed">⠿</Text>
          <Stack gap={2}>
            <Text size="sm" fw={500}>{art.title}</Text>
            <Text size="xs" c="dimmed">{art.slug}</Text>
          </Stack>
        </Group>
        <Group gap={4} wrap="nowrap">
          {isNext && <Badge color="teal" size="xs">Next up</Badge>}
          <PhaseBadge
            phase={art.phase}
            lastUpdate={art.last_update}
            running={claudeRunning}
            forceActivity={isActive}
          />
          <Tooltip label={claudeRunning ? 'Revision in progress' : 'Write this next'} withArrow>
            <ActionIcon
              size="xs"
              color="teal"
              variant="subtle"
              disabled={claudeRunning}
              onClick={() => onWriteNext(art.slug)}
            >
              ▶
            </ActionIcon>
          </Tooltip>
          <ActionIcon
            size="xs"
            color="red"
            variant="subtle"
            aria-label={`Remove ${art.slug} from cluster`}
            onClick={onRemove}
          >
            ✕
          </ActionIcon>
        </Group>
      </Group>
    </Box>
  )
}

export function ArticlesView() {
  const { data: queueData, isLoading } = useQueue()
  const saveQueue = useSaveQueue()
  const trigger = useTrigger()
  const approveArticle = useApproveArticle()
  const requestChanges = useRequestChanges()
  const deleteArticle = useDeleteArticle()
  const { openReader } = useReader()
  const { clusterId: selectedCluster, setClusterId } = useNavigation()

  const [localQueue, setLocalQueue] = useState<QueueData | null>(null)
  const [dirty, setDirty] = useState(false)
  const [newSlug, setNewSlug] = useState('')
  const [newTitle, setNewTitle] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)
  const [deleteArticleTarget, setDeleteArticleTarget] = useState<string | null>(null)

  const queue = localQueue ?? queueData
  const activeClusterId = selectedCluster ?? queue?.clusters[0]?.id ?? null
  const activeCluster = queue?.clusters.find((c) => c.id === activeClusterId)

  const { reviewable, plannable } = activeCluster
    ? partitionArticles(activeCluster.articles)
    : { reviewable: [], plannable: [] }

  const feedbackQueries = useQueries({
    queries: reviewable.map((art) => ({
      queryKey: ['feedback', art.slug],
      queryFn: () => apiFetch<{ slug: string; annotations: unknown[] }>(
        `/api/feedback?slug=${art.slug}`,
      ),
      staleTime: 5_000,
    })),
  })

  const commentCountBySlug = Object.fromEntries(
    reviewable.map((art, i) => [
      art.slug,
      feedbackQueries[i]?.data?.annotations?.length ?? 0,
    ]),
  )

  const nextPlannableSlug = plannable.find((a) => a.slug === queue?.next_slug)?.slug
    ?? plannable[0]?.slug
    ?? null

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  const markDirty = useCallback(
    (updater: (q: QueueData) => QueueData) => {
      setLocalQueue((prev) => {
        const base = prev ?? queueData
        if (!base) return prev
        return updater(JSON.parse(JSON.stringify(base)) as QueueData)
      })
      setDirty(true)
    },
    [queueData],
  )

  function updateCluster(patch: Partial<Cluster>) {
    if (!activeCluster) return
    markDirty((q) => ({
      ...q,
      clusters: q.clusters.map((c) =>
        c.id === activeCluster.id ? { ...c, ...patch } : c,
      ),
    }))
  }

  function handleDragEnd(event: DragEndEvent) {
    if (!activeCluster) return
    const { active, over } = event
    if (!over || active.id === over.id) return
    const plannableSlugs = plannable.map((a) => a.slug)
    const oldIndex = plannableSlugs.indexOf(String(active.id))
    const newIndex = plannableSlugs.indexOf(String(over.id))
    if (oldIndex < 0 || newIndex < 0) return

    markDirty((q) => ({
      ...q,
      clusters: q.clusters.map((c) => {
        if (c.id !== activeCluster.id) return c
        const { reviewable: rev, plannable: plan } = partitionArticles(c.articles)
        const reordered = arrayMove(plan, oldIndex, newIndex)
        return { ...c, articles: [...rev, ...reordered] }
      }),
    }))
  }

  function removeArticle(slug: string) {
    markDirty((q) => ({
      ...q,
      clusters: q.clusters.map((c) =>
        c.id === activeClusterId
          ? { ...c, articles: c.articles.filter((a) => a.slug !== slug) }
          : c,
      ),
    }))
    setDeleteTarget(null)
  }

  function confirmDeleteArticle(removeFromPlan: boolean) {
    const slug = deleteArticleTarget
    if (!slug) return
    deleteArticle.mutate(
      { slug, removeFromPlan },
      {
        onSuccess: (res: unknown) => {
          const r = res as { push_failed?: boolean }
          if (r?.push_failed) {
            notifications.show({
              title: 'Deleted (push failed)',
              message: `${slug} deleted locally but the push to main failed — retry needed`,
              color: 'orange',
            })
          } else {
            notifications.show({
              title: 'Deleted',
              message: `${slug} deleted${removeFromPlan ? ' and removed from plan' : ''}`,
              color: 'teal',
            })
          }
        },
        onError: (e) =>
          notifications.show({ title: 'Delete failed', message: e.message, color: 'red' }),
      },
    )
    setDeleteArticleTarget(null)
  }

  function addArticle() {
    if (!newSlug.trim() || !newTitle.trim()) return
    markDirty((q) => ({
      ...q,
      clusters: q.clusters.map((c) =>
        c.id === activeClusterId
          ? {
              ...c,
              articles: [
                ...c.articles,
                {
                  slug: newSlug.trim(),
                  title: newTitle.trim(),
                  phase: 'UNKNOWN',
                  revision_cycle: 0,
                  publish_stale: false,
                  feedback_issue: '',
                },
              ],
            }
          : c,
      ),
    }))
    setNewSlug('')
    setNewTitle('')
  }

  function handleSave() {
    if (!queue) return
    saveQueue.mutate(toPersistableQueue(queue) as QueueData, {
      onSuccess: () => {
        setDirty(false)
        setLocalQueue(null)
        notifications.show({ title: 'Saved', message: 'Queue updated', color: 'teal' })
      },
      onError: (e) =>
        notifications.show({ title: 'Error', message: e.message, color: 'red' }),
    })
  }

  function handleApprove(art: ArticleEntry) {
    modals.openConfirmModal({
      title: 'Approve and publish?',
      children: (
        <Text size="sm">
          Approve <strong>{art.slug}</strong> and publish to the catalog?
        </Text>
      ),
      labels: { confirm: 'Approve', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () =>
        approveArticle.mutate(
          { slug: art.slug, reviewer: 'reviewer' },
          {
            onSuccess: () =>
              notifications.show({
                title: 'Published',
                message: `${art.slug} approved and published`,
                color: 'green',
              }),
            onError: (e) =>
              notifications.show({ title: 'Approve failed', message: e.message, color: 'red' }),
          },
        ),
    })
  }

  function handleRequestChanges(art: ArticleEntry) {
    requestChanges.mutate(
      { slug: art.slug, reason: 'reviewer requested changes' },
      {
        onSuccess: () =>
          notifications.show({
            title: 'Sent back',
            message: `${art.slug} moved to REVISING`,
            color: 'orange',
          }),
        onError: (e) =>
          notifications.show({ title: 'Failed', message: e.message, color: 'red' }),
      },
    )
  }

  function handleWriteNext(slug: string) {
    modals.openConfirmModal({
      title: 'Write this next?',
      children: (
        <Text size="sm">
          Launch the article pipeline for <strong>{slug}</strong>?
        </Text>
      ),
      labels: { confirm: 'Write it', cancel: 'Cancel' },
      confirmProps: { color: 'teal' },
      onConfirm: () =>
        trigger.mutate(
          { slug, reason: 'manual' },
          {
            onSuccess: () =>
              notifications.show({ message: `Triggered ${slug}`, color: 'teal' }),
            onError: (e) =>
              notifications.show({ message: e.message, color: 'red' }),
          },
        ),
    })
  }

  function switchCluster(id: string) {
    if (dirty) {
      modals.openConfirmModal({
        title: 'Unsaved changes',
        children: <Text size="sm">Switch clusters without saving?</Text>,
        labels: { confirm: 'Switch', cancel: 'Stay' },
        onConfirm: () => {
          setClusterId(id)
          setDirty(false)
          setLocalQueue(null)
        },
      })
    } else {
      setClusterId(id)
    }
  }

  if (isLoading) return <Text c="dimmed" mt="xl" ta="center">Loading...</Text>
  if (!queue) return null

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Box>
          <Title order={3}>Articles</Title>
          <Text size="sm" c="dimmed">
            Review published articles and plan what&apos;s next
          </Text>
        </Box>
        <Group gap="xs">
          {dirty && <Badge color="orange">UNSAVED</Badge>}
          <Button
            onClick={handleSave}
            loading={saveQueue.isPending}
            disabled={!dirty}
            color="teal"
          >
            Save
          </Button>
        </Group>
      </Group>

      <Grid>
        <Grid.Col span={{ base: 12, sm: 3 }}>
          <Card withBorder p="xs">
            <Text size="xs" fw={600} c="dimmed" mb="xs">CLUSTERS</Text>
            {queue.clusters.map((c) => (
              <NavLink
                key={c.id}
                label={c.title}
                description={c.status}
                active={activeClusterId === c.id}
                onClick={() => switchCluster(c.id)}
                variant="filled"
                mb={2}
              />
            ))}
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 9 }}>
          {activeCluster ? (
            <Stack gap="md">
              <Card withBorder>
                <Stack gap="xs" mb="md">
                  <Group justify="space-between" wrap="wrap">
                    <Text fw={600}>{activeCluster.title}</Text>
                    <Group gap="xs" wrap="wrap">
                      <SegmentedControl
                        size="xs"
                        value={activeCluster.mode}
                        onChange={(v) => updateCluster({ mode: v as 'serial' | 'parallel' })}
                        data={[
                          { label: 'Serial', value: 'serial' },
                          { label: 'Parallel', value: 'parallel' },
                        ]}
                      />
                      <Select
                        size="xs"
                        w={100}
                        value={activeCluster.status}
                        onChange={(v) =>
                          updateCluster({ status: v as Cluster['status'] })
                        }
                        data={['active', 'paused', 'done']}
                      />
                      <Tooltip label="Pause auto-advance after last article merges">
                        <Switch
                          size="xs"
                          checked={activeCluster.pause_after ?? false}
                          onChange={(e) =>
                            updateCluster({ pause_after: e.currentTarget.checked })
                          }
                          label="Pause after"
                        />
                      </Tooltip>
                    </Group>
                  </Group>
                </Stack>

                <Text size="xs" fw={600} c="dimmed" mb="xs">WRITTEN & IN PROGRESS</Text>
                {reviewable.length === 0 ? (
                  <Text size="sm" c="dimmed" mb="md">No articles written yet.</Text>
                ) : (
                  reviewable.map((art) =>
                    art.phase === 'BLOCKED' ? (
                      <BlockedArticleRow
                        key={art.slug}
                        art={art}
                        onDelete={() => setDeleteArticleTarget(art.slug)}
                      />
                    ) : (
                      <ReviewArticleRow
                        key={art.slug}
                        art={art}
                        commentCount={commentCountBySlug[art.slug] ?? 0}
                        claudeRunning={
                          queue.claude_running &&
                          (!queue.active_article || queue.active_article === art.slug)
                        }
                        isActive={queue.active_article === art.slug}
                        onReview={() => openReader(art.slug)}
                        onApprove={() => handleApprove(art)}
                        onRequestChanges={() => handleRequestChanges(art)}
                        onDelete={() => setDeleteArticleTarget(art.slug)}
                      />
                    ),
                  )
                )}

                <Text size="xs" fw={600} c="dimmed" mt="lg" mb="xs">UP NEXT</Text>
                <DndContext
                  sensors={sensors}
                  collisionDetection={closestCenter}
                  onDragEnd={handleDragEnd}
                >
                  <SortableContext
                    items={plannable.map((a) => a.slug)}
                    strategy={verticalListSortingStrategy}
                  >
                    {plannable.length === 0 ? (
                      <Text size="sm" c="dimmed">Nothing planned — add an article below.</Text>
                    ) : (
                      plannable.map((art) => (
                        <SortableArticleRow
                          key={art.slug}
                          art={art}
                          isNext={art.slug === nextPlannableSlug}
                          claudeRunning={
                            queue.claude_running &&
                            (!queue.active_article || queue.active_article === art.slug)
                          }
                          isActive={queue.active_article === art.slug}
                          onRemove={() => setDeleteTarget(art.slug)}
                          onWriteNext={handleWriteNext}
                        />
                      ))
                    )}
                  </SortableContext>
                </DndContext>

                <Group mt="md" gap="xs">
                  <TextInput
                    size="xs"
                    placeholder="slug (NN-name)"
                    value={newSlug}
                    onChange={(e) => setNewSlug(e.currentTarget.value)}
                    style={{ flex: 1 }}
                  />
                  <TextInput
                    size="xs"
                    placeholder="Title"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.currentTarget.value)}
                    style={{ flex: 2 }}
                  />
                  <Button size="xs" onClick={addArticle} disabled={!newSlug || !newTitle}>
                    Add
                  </Button>
                </Group>

                {nextPlannableSlug && (
                  <Group mt="md" justify="flex-end">
                    <Tooltip
                      label="Revision in progress"
                      disabled={!queue.claude_running}
                      withArrow
                    >
                      <Button
                        size="sm"
                        color="teal"
                        loading={!!queue.claude_running}
                        disabled={!!queue.claude_running}
                        onClick={() => handleWriteNext(nextPlannableSlug)}
                      >
                        {queue.claude_running ? 'Revision in progress…' : `Write next → ${nextPlannableSlug}`}
                      </Button>
                    </Tooltip>
                  </Group>
                )}
              </Card>
            </Stack>
          ) : (
            <Text c="dimmed" ta="center" mt="xl">Select a cluster</Text>
          )}
        </Grid.Col>
      </Grid>

      <ConfirmDeleteModal
        opened={deleteTarget !== null}
        slug={deleteTarget ?? ''}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteTarget && removeArticle(deleteTarget)}
      />

      <DeleteArticleModal
        opened={deleteArticleTarget !== null}
        slug={deleteArticleTarget ?? ''}
        onClose={() => setDeleteArticleTarget(null)}
        onConfirm={confirmDeleteArticle}
      />
    </Stack>
  )
}
