export type StoredProfile = {
  displayName?: string
  photoDataUrl?: string | null
  sport?: string
  focusArea?: string
  dateOfBirth?: string
}

const PROFILE_EVENT = 'hamsai-profile-updated'
const PROFILE_PREFIX = 'hamsai-profile:'

function getProfileKey(email: string) {
  return `${PROFILE_PREFIX}${email.toLowerCase()}`
}

export function getStoredProfile(email: string): StoredProfile {
  if (typeof window === 'undefined') {
    return {}
  }

  const raw = window.localStorage.getItem(getProfileKey(email))
  if (!raw) {
    return {}
  }

  try {
    return JSON.parse(raw) as StoredProfile
  } catch {
    window.localStorage.removeItem(getProfileKey(email))
    return {}
  }
}

export function saveStoredProfile(email: string, profile: StoredProfile) {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(getProfileKey(email), JSON.stringify(profile))
  window.dispatchEvent(new CustomEvent(PROFILE_EVENT, { detail: { email } }))
}

export function subscribeToStoredProfile(callback: (email?: string) => void) {
  if (typeof window === 'undefined') {
    return () => undefined
  }

  const handleStorage = (event: StorageEvent) => {
    if (event.key?.startsWith(PROFILE_PREFIX)) {
      callback(event.key.replace(PROFILE_PREFIX, ''))
    }
  }

  const handleCustom = (event: Event) => {
    const customEvent = event as CustomEvent<{ email?: string }>
    callback(customEvent.detail?.email)
  }

  window.addEventListener('storage', handleStorage)
  window.addEventListener(PROFILE_EVENT, handleCustom)

  return () => {
    window.removeEventListener('storage', handleStorage)
    window.removeEventListener(PROFILE_EVENT, handleCustom)
  }
}
