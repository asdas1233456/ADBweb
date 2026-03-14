export type GuideKey =
  | 'dashboard'
  | 'devices'
  | 'device-health'
  | 'scripts'
  | 'scheduled'
  | 'ai-script'
  | 'ai-element-locator'
  | 'reports'
  | 'failure-analysis'
  | 'activity-log'
  | 'workspace'
  | 'tasks'


export const GUIDE_VERSION = '2026-03-15'
const STORAGE_KEY = 'adbweb_guide_state'
export const GUIDE_START_EVENT = 'adbweb:guide:start'

type GuideState = Record<string, { version?: string; completedAt?: string }>

function loadState(): GuideState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as GuideState) : {}
  } catch {
    return {}
  }
}

function saveState(state: GuideState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // ignore
  }
}

export function isGuideCompleted(key: GuideKey): boolean {
  const state = loadState()
  return state[key]?.version === GUIDE_VERSION
}

export function markGuideCompleted(key: GuideKey) {
  const state = loadState()
  state[key] = { version: GUIDE_VERSION, completedAt: new Date().toISOString() }
  saveState(state)
}

export function resetGuide(key: GuideKey) {
  const state = loadState()
  delete state[key]
  saveState(state)
}

export function startGuide(key: GuideKey) {
  window.dispatchEvent(new CustomEvent(GUIDE_START_EVENT, { detail: { key } }))
}

export function getGuideKeyForPath(pathname: string): GuideKey | null {
  if (pathname === '/' || pathname === '/dashboard') return 'dashboard'
  if (pathname.startsWith('/devices')) return 'devices'
  if (pathname.startsWith('/device-health')) return 'device-health'
  if (pathname.startsWith('/scripts')) return 'scripts'
  if (pathname.startsWith('/scheduled')) return 'scheduled'
  if (pathname.startsWith('/ai-script')) return 'ai-script'
  if (pathname.startsWith('/ai-element-locator')) return 'ai-element-locator'
  if (pathname.startsWith('/reports')) return 'reports'
  if (pathname.startsWith('/failure-analysis')) return 'failure-analysis'
  if (pathname.startsWith('/activity-log')) return 'activity-log'
  if (pathname.startsWith('/workspace')) return 'workspace'
  if (pathname.startsWith('/tasks')) return 'tasks'
  return null
}
