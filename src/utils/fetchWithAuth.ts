export function getApiKey(): string {
  try {
    return (
      localStorage.getItem('api_access_key') ||
      (import.meta as any).env?.VITE_API_ACCESS_KEY ||
      ''
    )
  } catch {
    return ''
  }
}

export function buildAuthHeaders(): Record<string, string> {
  const key = getApiKey()
  return key ? { 'X-API-Key': key } : {}
}

export async function fetchWithAuth(input: RequestInfo, init?: RequestInit) {
  const headers = new Headers(init?.headers || {})
  const authHeaders = buildAuthHeaders()
  Object.entries(authHeaders).forEach(([k, v]) => headers.set(k, v))

  return fetch(input, {
    ...init,
    headers,
  })
}

export function buildWsUrl(baseUrl: string, clientId?: string) {
  const key = getApiKey()
  const url = clientId ? `${baseUrl}/${clientId}` : baseUrl
  if (!key) return url
  const sep = url.includes('?') ? '&' : '?'
  return `${url}${sep}api_key=${encodeURIComponent(key)}`
}
