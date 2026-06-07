import { Modal, Text, TextInput, Button, Group } from '@mantine/core'
import { useState, useEffect } from 'react'

export interface ConfirmDeleteModalProps {
  opened: boolean
  slug: string
  onClose: () => void
  onConfirm: () => void
}

export function ConfirmDeleteModal({
  opened,
  slug,
  onClose,
  onConfirm,
}: ConfirmDeleteModalProps) {
  const [confirmText, setConfirmText] = useState('')

  useEffect(() => {
    if (!opened) setConfirmText('')
  }, [opened])

  const canConfirm = confirmText === 'delete'

  return (
    <Modal opened={opened} onClose={onClose} title="Remove article from cluster?" centered>
      <Text size="sm" mb="md">
        Type <strong>delete</strong> to remove <strong>{slug}</strong> from this cluster.
      </Text>
      <TextInput
        placeholder="delete"
        value={confirmText}
        onChange={(e) => setConfirmText(e.currentTarget.value)}
        data-testid="delete-confirm-input"
        mb="md"
      />
      <Group justify="flex-end">
        <Button variant="default" onClick={onClose}>Cancel</Button>
        <Button color="red" disabled={!canConfirm} onClick={onConfirm}>
          Confirm delete
        </Button>
      </Group>
    </Modal>
  )
}
