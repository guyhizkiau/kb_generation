import {
  Box, Button, Card, Group, Stack, Text, TextInput, Title, Badge,
  ActionIcon, PasswordInput, Divider,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { IconPlus, IconTrash, IconRefresh, IconDeviceFloppy } from '@tabler/icons-react'
import { useEffect, useState } from 'react'
import { useTestConfig, useSaveTestConfig, type TestConfigData } from '@/api/hooks'
import {
  generateFileList,
  generateFileName,
  generateFolderFiles,
  generateFolderName,
  roleLabel,
  suggestRoleKey,
} from '@/lib/testConfigNames'

export interface UserFields {
  email: string
  email_password?: string
  specterx_password?: string
  has_email_password?: boolean
  has_specterx_password?: boolean
}

export interface TestConfigForm {
  users: Record<string, UserFields>
  files: {
    default: string
    list: string[]
    folder: string
    folder_files: string[]
  }
}

function emptyForm(): TestConfigForm {
  return {
    users: {
      data_owner: { email: '', email_password: '', specterx_password: '' },
      recipient: { email: '', email_password: '', specterx_password: '' },
    },
    files: {
      default: 'test-document.pdf',
      list: ['test-document.pdf', 'test-document-2.pdf', 'test-document-3.pdf'],
      folder: 'sample-folder',
      folder_files: ['doc-a.pdf', 'doc-b.pdf', 'notes.txt'],
    },
  }
}

function fromApi(data: TestConfigData): TestConfigForm {
  const base = emptyForm()
  const users: Record<string, UserFields> = { ...base.users }
  for (const [role, fields] of Object.entries(data.users ?? {})) {
    if (role === 'recipient_gmail') continue
    users[role] = {
      email: fields.email ?? '',
      email_password: '',
      specterx_password: '',
      has_email_password: fields.has_email_password,
      has_specterx_password: fields.has_specterx_password,
    }
  }
  return {
    users,
    files: { ...base.files, ...data.files },
  }
}

export function SettingsView() {
  const { data, isLoading, error } = useTestConfig()
  const save = useSaveTestConfig()
  const [form, setForm] = useState<TestConfigForm>(emptyForm)
  const [newRoleLabel, setNewRoleLabel] = useState('')

  useEffect(() => {
    if (data) setForm(fromApi(data))
  }, [data])

  const updateUser = (role: string, patch: Partial<UserFields>) => {
    setForm((prev) => ({
      ...prev,
      users: {
        ...prev.users,
        [role]: { ...prev.users[role], ...patch },
      },
    }))
  }

  const removeUser = (role: string) => {
    if (['data_owner', 'recipient'].includes(role)) return
    setForm((prev) => {
      const next = { ...prev.users }
      delete next[role]
      return { ...prev, users: next }
    })
  }

  const addUser = () => {
    const key = suggestRoleKey(newRoleLabel || 'custom account')
    if (form.users[key]) {
      notifications.show({ title: 'Role exists', message: key, color: 'red' })
      return
    }
    setForm((prev) => ({
      ...prev,
      users: {
        ...prev.users,
        [key]: { email: '', email_password: '', specterx_password: '' },
      },
    }))
    setNewRoleLabel('')
  }

  const handleSave = () => {
    save.mutate(form, {
      onSuccess: () =>
        notifications.show({
          title: 'Saved',
          message: 'Test resources updated',
          color: 'teal',
        }),
      onError: (err) =>
        notifications.show({
          title: 'Save failed',
          message: String(err),
          color: 'red',
        }),
    })
  }

  if (isLoading) return <Text c="dimmed" mt="xl" ta="center">Loading settings...</Text>
  if (error) return <Text c="red" mt="xl" ta="center">Error loading test config</Text>

  return (
    <Stack gap="lg" maw={720}>
      <Group justify="space-between" align="flex-start">
        <Box>
          <Title order={3}>Test resources</Title>
          <Text size="sm" c="dimmed">
            Email accounts are the primary credentials. SpecterX passwords are optional —
            leave empty and the next test run sets one via the reset-password flow.
          </Text>
        </Box>
        <Button
          leftSection={<IconDeviceFloppy size={16} />}
          onClick={handleSave}
          loading={save.isPending}
        >
          Save
        </Button>
      </Group>

      <Card withBorder padding="lg" radius="md">
        <Title order={5} mb="md">Users &amp; credentials</Title>
        <Stack gap="md">
          {Object.entries(form.users).map(([role, fields]) => (
            <Card key={role} withBorder padding="md" radius="sm" bg="gray.0">
              <Group justify="space-between" mb="xs">
                <Group gap="xs">
                  <Text fw={600} size="sm">{roleLabel(role)}</Text>
                  <Badge size="xs" variant="light">{role}</Badge>
                </Group>
                {!['data_owner', 'recipient'].includes(role) && (
                  <ActionIcon
                    variant="subtle"
                    color="red"
                    aria-label={`Remove ${role}`}
                    onClick={() => removeUser(role)}
                  >
                    <IconTrash size={16} />
                  </ActionIcon>
                )}
              </Group>
              <Stack gap="xs">
                <TextInput
                  label="Email address"
                  description="SpecterX login email and mailbox for verification messages."
                  value={fields.email}
                  onChange={(e) => updateUser(role, { email: e.currentTarget.value })}
                  placeholder="account@specterx.com"
                />
                <PasswordInput
                  label="Email account password"
                  description="Gmail / Google Workspace mailbox password — used to read verification emails and reset SpecterX passwords."
                  value={fields.email_password ?? ''}
                  onChange={(e) => updateUser(role, { email_password: e.currentTarget.value })}
                  placeholder={
                    fields.has_email_password ? '(unchanged — enter to replace)' : 'Mailbox password'
                  }
                />
                <PasswordInput
                  label="SpecterX password"
                  description="Optional. Leave empty and the next test run will set one automatically via reset-password."
                  value={fields.specterx_password ?? ''}
                  onChange={(e) => updateUser(role, { specterx_password: e.currentTarget.value })}
                  placeholder={
                    fields.has_specterx_password
                      ? '(unchanged — enter to replace)'
                      : 'Auto-set on next run if empty'
                  }
                />
              </Stack>
            </Card>
          ))}

          <Divider label="Add account" labelPosition="center" />
          <Group align="flex-end">
            <TextInput
              label="New account label"
              placeholder="e.g. External reviewer"
              value={newRoleLabel}
              onChange={(e) => setNewRoleLabel(e.currentTarget.value)}
              style={{ flex: 1 }}
            />
            <Button leftSection={<IconPlus size={16} />} variant="light" onClick={addUser}>
              Add
            </Button>
          </Group>
        </Stack>
      </Card>

      <Card withBorder padding="lg" radius="md">
        <Title order={5} mb="md">Upload file names</Title>
        <Stack gap="md">
          <Group align="flex-end" wrap="nowrap">
            <TextInput
              label="Default file (single upload)"
              value={form.files.default}
              onChange={(e) =>
                setForm((prev) => ({
                  ...prev,
                  files: { ...prev.files, default: e.currentTarget.value },
                }))
              }
              style={{ flex: 1 }}
            />
            <Button
              variant="light"
              leftSection={<IconRefresh size={16} />}
              onClick={() =>
                setForm((prev) => ({
                  ...prev,
                  files: { ...prev.files, default: generateFileName('pdf') },
                }))
              }
            >
              Generate
            </Button>
          </Group>

          <Box>
            <Group justify="space-between" mb="xs">
              <Text size="sm" fw={500}>Multi-file list</Text>
              <Group gap="xs">
                <Button
                  size="xs"
                  variant="light"
                  leftSection={<IconPlus size={14} />}
                  onClick={() =>
                    setForm((prev) => ({
                      ...prev,
                      files: {
                        ...prev.files,
                        list: [...prev.files.list, generateFileName('pdf')],
                      },
                    }))
                  }
                >
                  Add row
                </Button>
                <Button
                  size="xs"
                  variant="light"
                  leftSection={<IconRefresh size={14} />}
                  onClick={() =>
                    setForm((prev) => ({
                      ...prev,
                      files: { ...prev.files, list: generateFileList(3, 'pdf') },
                    }))
                  }
                >
                  Generate list
                </Button>
              </Group>
            </Group>
            <Stack gap="xs">
              {form.files.list.map((name, idx) => (
                <Group key={`list-${idx}`} gap="xs" wrap="nowrap">
                  <TextInput
                    value={name}
                    onChange={(e) => {
                      const next = [...form.files.list]
                      next[idx] = e.currentTarget.value
                      setForm((prev) => ({
                        ...prev,
                        files: { ...prev.files, list: next },
                      }))
                    }}
                    style={{ flex: 1 }}
                  />
                  <ActionIcon
                    variant="subtle"
                    color="red"
                    aria-label="Remove file"
                    onClick={() =>
                      setForm((prev) => ({
                        ...prev,
                        files: {
                          ...prev.files,
                          list: prev.files.list.filter((_, i) => i !== idx),
                        },
                      }))
                    }
                  >
                    <IconTrash size={16} />
                  </ActionIcon>
                </Group>
              ))}
            </Stack>
          </Box>

          <Group align="flex-end" wrap="nowrap">
            <TextInput
              label="Folder name"
              value={form.files.folder}
              onChange={(e) =>
                setForm((prev) => ({
                  ...prev,
                  files: { ...prev.files, folder: e.currentTarget.value },
                }))
              }
              style={{ flex: 1 }}
            />
            <Button
              variant="light"
              leftSection={<IconRefresh size={16} />}
              onClick={() =>
                setForm((prev) => ({
                  ...prev,
                  files: { ...prev.files, folder: generateFolderName() },
                }))
              }
            >
              Generate
            </Button>
          </Group>

          <Box>
            <Group justify="space-between" mb="xs">
              <Text size="sm" fw={500}>Files inside folder</Text>
              <Button
                size="xs"
                variant="light"
                leftSection={<IconRefresh size={14} />}
                onClick={() =>
                  setForm((prev) => ({
                    ...prev,
                    files: { ...prev.files, folder_files: generateFolderFiles(3) },
                  }))
                }
              >
                Generate list
              </Button>
            </Group>
            <Stack gap="xs">
              {form.files.folder_files.map((name, idx) => (
                <Group key={`folder-${idx}`} gap="xs" wrap="nowrap">
                  <TextInput
                    value={name}
                    onChange={(e) => {
                      const next = [...form.files.folder_files]
                      next[idx] = e.currentTarget.value
                      setForm((prev) => ({
                        ...prev,
                        files: { ...prev.files, folder_files: next },
                      }))
                    }}
                    style={{ flex: 1 }}
                  />
                  <ActionIcon
                    variant="subtle"
                    color="red"
                    aria-label="Remove folder file"
                    onClick={() =>
                      setForm((prev) => ({
                        ...prev,
                        files: {
                          ...prev.files,
                          folder_files: prev.files.folder_files.filter((_, i) => i !== idx),
                        },
                      }))
                    }
                  >
                    <IconTrash size={16} />
                  </ActionIcon>
                </Group>
              ))}
            </Stack>
          </Box>
        </Stack>
      </Card>
    </Stack>
  )
}
