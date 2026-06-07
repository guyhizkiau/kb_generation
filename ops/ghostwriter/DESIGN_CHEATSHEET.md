# Design Cheatsheet — Ghostwriter SPA

## Brand palette

| Token | Value | Usage |
|---|---|---|
| Primary teal | #023632 | CTA buttons, active state, accent |
| Canvas white | #F8F8FA | Page background (`white` in Mantine theme) |
| Card border | rgba(0,0,0,0.06) | Card and panel borders |
| Neutral text | #1C1C1E | Body copy |
| Dimmed text | #57606a | Labels, meta, captions |

## Spacing

- Card radius: `md` (10px in Mantine)
- Control radius: `sm` (4px)
- Section gap: 16px (`gap="md"`)
- Inner card padding: 16px (`p="md"`)
- Compact card: `p="xs"` (e.g. cluster selector sidebar)

## Typography

- Font: Inter (fallback: system-ui, -apple-system, sans-serif)
- Headings: `fw={600}` or `fw={700}`
- Body: default weight, `size="sm"` (14px)
- Labels/meta: `size="xs"` + `c="dimmed"`
- Code/mono: `<Code>` component (Mantine, uses JetBrains Mono / monospace stack)

## Layout patterns

### Master-detail (Queue + Feedback views)
- Left column (`span={{ base: 12, sm: 3 }}`): cluster/article list as `NavLink` items
  inside a compact `Card withBorder p="xs"`.
- Selected item: `variant="filled"` (fills with primary teal).
- Right column (`span={{ base: 12, sm: 9 }}`): detail `Card withBorder`.

### Dirty guard (Queue view)
1. When unsaved changes exist, show `<Badge color="orange">UNSAVED</Badge>` near Save.
2. On nav away (cluster switch): `modals.openConfirmModal` asking whether to discard.
3. On save success: clear dirty state + `setLocalQueue(null)` to revert to server data.

### Phase badges
`<Badge color={PHASE_COLORS[phase]} variant="light" size="sm">` — never `variant="filled"`
for phase (that's reserved for selected nav items).

### PUBLISH_STALE
Always `<Badge color="orange" size="xs">STALE</Badge>` — both Queue and Feedback views.

### Drag handles
Character `⠿` with `style={{ cursor: 'grab' }}` on the drag-listeners group.

## Mantine component defaults

| Component | Default variant | Notes |
|---|---|---|
| `NavLink` | `variant="filled"` when active | Compact cluster list |
| `Badge` | `variant="light"` | For phases; `variant="filled"` for status hero |
| `Button` | `color="teal"` for primary actions | |
| `Card` | `withBorder` | Always — matches neutral border token |
| `Table` | `striped highlightOnHover` | For PRs, failed comments |
| `notifications.show` | `color: 'teal'` success, `color: 'red'` error | |
| `modals.openConfirmModal` | `confirmProps: { color: 'teal' }` | Dirty guard, trigger confirms |

## Data refresh intervals

- Daemon status (`/status.json`): 5 s
- Queue (`/api/queue`): 10 s
- Feedback: on-demand (triggered by slug selection)
