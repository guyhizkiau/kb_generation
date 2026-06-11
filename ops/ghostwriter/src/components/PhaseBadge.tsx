import { Badge, Tooltip } from '@mantine/core'
import { formatPhaseElapsed, PIPELINE_ACTIVITY_PHASES } from '@/lib/articlePhase'
import styles from './PhaseBadge.module.css'

const PHASE_COLORS: Record<string, string> = {
  PLANNED: 'gray',
  DRAFTING: 'blue',
  TESTING: 'yellow',
  REVISING: 'orange',
  FINALIZING: 'violet',
  PR_OPEN: 'cyan',
  IN_REVIEW: 'cyan',
  APPROVED: 'teal',
  MERGED: 'teal',
  DONE: 'green',
  PUBLISHED: 'green',
  BLOCKED: 'red',
  UNKNOWN: 'gray',
}

export interface PhaseBadgeProps {
  phase: string
  lastUpdate?: string
  running?: boolean
}

/**
 * Pipeline phase badge with optional elapsed-time and running/idle indicator
 * for automated pipeline phases (not human-review gates like IN_REVIEW).
 */
export function PhaseBadge({ phase, lastUpdate, running }: PhaseBadgeProps) {
  const color = PHASE_COLORS[phase] ?? 'gray'
  const showActivity = PIPELINE_ACTIVITY_PHASES.has(phase)
  const elapsed = showActivity && lastUpdate ? formatPhaseElapsed(lastUpdate) : null
  const isIdle = running === false && showActivity

  let label = phase
  if (elapsed && isIdle) {
    label = `${phase} · idle · ${elapsed}`
  } else if (elapsed) {
    label = `${phase} · ${elapsed}`
  } else if (isIdle) {
    label = `${phase} · idle`
  }

  const tooltip =
    elapsed && running === true
      ? `Running for ${elapsed}`
      : elapsed && isIdle
        ? `Idle for ${elapsed}`
        : undefined

  const badge = (
    <Badge color={color} variant="light" size="sm" className={styles.phaseBadge}>
      {running === true && showActivity && (
        <span
          className={`${styles.phaseBadge__dot} ${styles['phaseBadge__dot--running']}`}
          aria-hidden
        />
      )}
      {label}
    </Badge>
  )

  if (tooltip) {
    return <Tooltip label={tooltip}>{badge}</Tooltip>
  }

  return badge
}
