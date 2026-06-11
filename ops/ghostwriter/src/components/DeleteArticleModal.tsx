import { Modal, Text, TextInput, Button, Group, Stack } from '@mantine/core'
import { useState, useEffect } from 'react'

export interface DeleteArticleModalProps {
  opened: boolean
  slug: string
  onClose: () => void
  onConfirm: (removeFromPlan: boolean) => void
}

export function DeleteArticleModal({
  opened,
  slug,
  onClose,
  onConfirm,
}: DeleteArticleModalProps) {
  const [confirmText, setConfirmText] = useState('')

  useEffect(() => {
    if (!opened) setConfirmText('')
  }, [opened])

  const canConfirm = confirmText === 'delete'

  return (
    <Modal opened={opened} onClose={onClose} title="Delete article?" centered>
      <Text size="sm" mb="xs">
        This permanently deletes the files for <strong>{slug}</strong> from{' '}
        <strong>main</strong>.
      </Text>
      <Text size="sm" mb="md">
        <strong>Delete article</strong> keeps the slug in the plan — the pipeline
        will treat it as queued and rewrite it on the next run.
        <br />
        <strong>Delete &amp; remove from plan</strong> also drops it from{' '}
        <strong>clusters/queue.json</strong>.
        <br />
        Type <strong>delete</strong> to confirm.
      </Text>
      <TextInput
        placeholder="delete"
        value={confirmText}
        onChange={(e) => setConfirmText(e.currentTarget.value)}
        data-testid="delete-confirm-input"
        mb="md"
      />
      <Stack gap="xs">
        <Group justify="flex-end" gap="xs">
          <Button variant="default" onClick={onClose}>Cancel</Button>
          <Button
            color="red"
            variant="light"
            disabled={!canConfirm}
            onClick={() => onConfirm(false)}
          >
            Delete article
          </Button>
          <Button
            color="red"
            disabled={!canConfirm}
            onClick={() => onConfirm(true)}
          >
            Delete &amp; remove from plan
          </Button>
        </Group>
      </Stack>
    </Modal>
  )
}
