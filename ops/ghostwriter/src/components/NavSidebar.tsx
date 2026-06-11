import {
  Box, Text, Tooltip, UnstyledButton, Group, Burger, Stack,
} from '@mantine/core'
import {
  IconFileText, IconActivity, IconMessageCircle, IconSettings,
  IconChevronLeft, IconChevronRight,
} from '@tabler/icons-react'

export type AppView = 'articles' | 'health' | 'feedback' | 'settings'

const NAV_ITEMS: { id: AppView; label: string; Icon: typeof IconFileText }[] = [
  { id: 'articles', label: 'Articles', Icon: IconFileText },
  { id: 'health', label: 'Health', Icon: IconActivity },
  { id: 'feedback', label: 'Feedback', Icon: IconMessageCircle },
  { id: 'settings', label: 'Settings', Icon: IconSettings },
]

export interface NavSidebarProps {
  active: AppView
  onSelect: (view: AppView) => void
  collapsed: boolean
  onToggleCollapse: () => void
  mobileOpened: boolean
  onMobileToggle: () => void
}

export function NavSidebar({
  active,
  onSelect,
  collapsed,
  onToggleCollapse,
  mobileOpened,
  onMobileToggle,
}: NavSidebarProps) {
  return (
    <Stack h="100%" justify="space-between" gap={0}>
      <Box>
        <Group px="sm" py="md" justify={collapsed ? 'center' : 'space-between'} wrap="nowrap">
          {!collapsed && (
            <Box>
              <Text fw={700} size="sm" c="teal.8">SpecterX Ghostwriter</Text>
            </Box>
          )}
          {collapsed && (
            <Text fw={700} size="sm" c="teal.8">GW</Text>
          )}
          <Burger opened={mobileOpened} onClick={onMobileToggle} hiddenFrom="sm" size="sm" />
        </Group>

        <Stack gap={4} px="xs">
          {NAV_ITEMS.map(({ id, label, Icon }) => {
            const isActive = active === id
            const btn = (
              <UnstyledButton
                key={id}
                onClick={() => onSelect(id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: collapsed ? 0 : 10,
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  width: '100%',
                  padding: collapsed ? '12px 0' : '10px 12px',
                  borderRadius: 6,
                  borderLeft: isActive ? '3px solid #023632' : '3px solid transparent',
                  background: isActive ? 'rgba(2,54,50,0.07)' : 'transparent',
                  fontWeight: isActive ? 600 : 400,
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.background = '#F5F5F5'
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'transparent'
                }}
              >
                <Icon size={20} stroke={1.5} color={isActive ? '#023632' : '#666'} />
                {!collapsed && (
                  <Text size="sm" c={isActive ? 'teal.9' : 'dark'}>{label}</Text>
                )}
              </UnstyledButton>
            )
            return collapsed ? (
              <Tooltip key={id} label={label} position="right">
                {btn}
              </Tooltip>
            ) : btn
          })}
        </Stack>
      </Box>

      <Box p="xs">
        <Tooltip label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'} position="right" disabled={!collapsed}>
          <UnstyledButton
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            onClick={onToggleCollapse}
            visibleFrom="sm"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'flex-start',
              gap: 8,
              width: '100%',
              padding: collapsed ? '12px 0' : '10px 12px',
              borderRadius: 6,
            }}
          >
            {collapsed ? <IconChevronRight size={18} /> : (
              <>
                <IconChevronLeft size={18} />
                <Text size="xs" c="dimmed">Collapse</Text>
              </>
            )}
          </UnstyledButton>
        </Tooltip>
      </Box>
    </Stack>
  )
}
