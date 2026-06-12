import { useState, useEffect, useRef } from 'react'
import {
  Box, Group, Text, Button, Title, Skeleton, Stack, Tabs, Textarea, ScrollArea, Alert,
} from '@mantine/core'
import { IconArrowLeft } from '@tabler/icons-react'
import { notifications } from '@mantine/notifications'
import { modals } from '@mantine/modals'
import { useQueryClient } from '@tanstack/react-query'
import {
  useDocs, useDoc, useSaveDoc, useFeedback, useReviseDoc, useDismissAnnotation, docPreviewUrl,
} from '@/api/hooks'
import { AnnotationCard } from '@/components/AnnotationCard'

type PreviewState = 'loading' | 'ready'

export interface DocReaderOverlayProps {
  docId: string
  onClose: () => void
}

export function DocReaderOverlay({ docId, onClose }: DocReaderOverlayProps) {
  const queryClient = useQueryClient()
  const feedbackSlug = `doc--${docId}`
  const { data: docsData } = useDocs()
  const { data, isError } = useDoc(docId)
  const { data: feedbackData, isLoading: fbLoading, refetch } = useFeedback(feedbackSlug)
  const saveDoc = useSaveDoc()
  const reviseDoc = useReviseDoc()
  const dismissAnnotation = useDismissAnnotation()
  const [previewState, setPreviewState] = useState<PreviewState>('loading')
  const [draft, setDraft] = useState('')
  const [justTriggered, setJustTriggered] = useState(false)
  const prevPending = useRef(false)

  const docMeta = docsData?.docs.find((d) => d.id === docId)
  const title = docMeta?.title ?? docId
  const activeAnnotations = feedbackData?.annotations ?? []
  const revisionInProgress = justTriggered || reviseDoc.isPending

  useEffect(() => {
    setPreviewState('loading')
  }, [docId])

  useEffect(() => {
    if (data?.content !== undefined) {
      setDraft(data.content)
    }
  }, [data?.content])

  useEffect(() => {
    if (prevPending.current && !reviseDoc.isPending) setJustTriggered(false)
    prevPending.current = reviseDoc.isPending
  }, [reviseDoc.isPending])

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const msg = event.data as { type?: string; slug?: string } | null
      if (msg?.type === 'ghostwriter:annotation-created' && msg.slug === feedbackSlug) {
        refetch()
        queryClient.invalidateQueries({ queryKey: ['feedback', feedbackSlug] })
      }
    }
    window.addEventListener('message', onMessage)
    return () => window.removeEventListener('message', onMessage)
  }, [feedbackSlug, refetch, queryClient])

  function handleClose() {
    if (data?.content !== undefined && draft !== data.content) {
      if (!window.confirm('You have unsaved changes. Close anyway?')) return
    }
    onClose()
  }

  function handleAccept() {
    modals.openConfirmModal({
      title: 'Accept this feedback?',
      children: (
        <Text size="sm">
          Launch <strong>revise-doc</strong> for <strong>{title}</strong>?
        </Text>
      ),
      labels: { confirm: 'Launch revision', cancel: 'Cancel' },
      confirmProps: { color: 'teal' },
      onConfirm: () =>
        reviseDoc.mutate(docId, {
          onSuccess: () => {
            setJustTriggered(true)
            notifications.show({
              title: 'Launched',
              message: `Revision started for ${title}`,
              color: 'teal',
            })
          },
          onError: (e) =>
            notifications.show({ title: 'Error', message: e.message, color: 'red' }),
        }),
    })
  }

  function handleSave() {
    saveDoc.mutate(
      { id: docId, content: draft },
      {
        onSuccess: () => {
          notifications.show({
            title: 'Saved',
            message: `${title} updated`,
            color: 'teal',
          })
        },
        onError: (e) => {
          notifications.show({ title: 'Save failed', message: e.message, color: 'red' })
        },
      },
    )
  }

  const dirty = data?.content !== undefined && draft !== data.content

  return (
    <Box
      data-testid="doc-reader-overlay"
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
          <Button variant="subtle" leftSection={<IconArrowLeft size={16} />} onClick={handleClose}>
            Back
          </Button>
          <Box>
            <Title order={4}>{title}</Title>
            <Text size="xs" c="dimmed">{docMeta?.path ?? docId}</Text>
          </Box>
        </Group>
        {activeAnnotations.length > 0 && (
          <Button size="sm" color="teal" disabled={revisionInProgress} onClick={handleAccept}>
            Accept feedback
          </Button>
        )}
      </Group>

      <Box style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <Tabs defaultValue="preview" style={{ flex: 3, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <Tabs.List px="md">
            <Tabs.Tab value="preview">Preview</Tabs.Tab>
            <Tabs.Tab value="edit">Edit</Tabs.Tab>
          </Tabs.List>
          <Tabs.Panel value="preview" style={{ flex: 1, minHeight: 0 }}>
            <Box style={{ position: 'relative', width: '100%', height: '100%' }}>
              {previewState === 'loading' && (
                <Stack p="md" gap="sm" style={{ position: 'absolute', inset: 0, zIndex: 1, background: '#fff' }}>
                  <Skeleton height={28} width="60%" />
                  <Skeleton height={200} />
                </Stack>
              )}
              <iframe
                title={`Preview: ${docId}`}
                src={docPreviewUrl(docId)}
                onLoad={() => setPreviewState('ready')}
                style={{ width: '100%', height: '100%', border: 'none', background: '#fff', minHeight: 480 }}
              />
            </Box>
          </Tabs.Panel>
          <Tabs.Panel value="edit" p="md" style={{ flex: 1, overflow: 'auto' }}>
            {isError && <Text c="red" mb="sm">Could not load document</Text>}
            <Textarea
              value={draft}
              onChange={(e) => setDraft(e.currentTarget.value)}
              minRows={20}
              autosize
              styles={{ input: { fontFamily: 'monospace' } }}
            />
            <Button mt="md" color="teal" disabled={!dirty || saveDoc.isPending} onClick={handleSave}>
              Save
            </Button>
          </Tabs.Panel>
        </Tabs>

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
                    { slug: feedbackSlug, id: ann.id },
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
              Claude is revising this document from your feedback.
            </Alert>
          )}
        </ScrollArea>
      </Box>
    </Box>
  )
}
