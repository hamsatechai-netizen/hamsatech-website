import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getCoachProfile, updateCoachProfile, type CoachProfile } from '../lib/authApi'
import { getStoredProfile, saveStoredProfile } from '../lib/profileStorage'
import '../styles/Profile.css'

function ProfilePage() {
  const { user, isLoading } = useAuth()
  const [displayName, setDisplayName] = useState('')
  const [photoDataUrl, setPhotoDataUrl] = useState<string | null>(null)
  const [sport, setSport] = useState('')
  const [focusArea, setFocusArea] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [phone, setPhone] = useState('')
  const [specialization, setSpecialization] = useState('')
  const [coachStatus, setCoachStatus] = useState<'active' | 'inactive'>('active')
  const [coachProfile, setCoachProfile] = useState<CoachProfile | null>(null)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    if (!user?.email) {
      return
    }

    const storedProfile = getStoredProfile(user.email)
    setDisplayName(storedProfile.displayName?.trim() || user.fullName)
    setPhotoDataUrl(storedProfile.photoDataUrl ?? null)
    setSport(storedProfile.sport ?? user.sport ?? '')
    setFocusArea(storedProfile.focusArea ?? user.focusArea ?? '')
    setDateOfBirth(storedProfile.dateOfBirth ?? user.dateOfBirth ?? '')

    if (user.role === 'coach') {
      void getCoachProfile()
        .then((profile) => {
          setCoachProfile(profile)
          setDisplayName(profile.name || user.fullName)
          setPhone(profile.phone ?? '')
          setSpecialization(profile.specialization ?? '')
          setCoachStatus(profile.status)
        })
        .catch(() => undefined)
    }
  }, [user?.dateOfBirth, user?.email, user?.focusArea, user?.fullName, user?.sport])

  if (!isLoading && !user) {
    return <Navigate to="/signin" replace state={{ from: { pathname: '/profile' } }} />
  }

  if (!user) {
    return null
  }

  const renderAvatarFallback = () => (
    <svg viewBox="0 0 64 64" aria-hidden="true" className="profile-page-avatar-icon">
      <circle cx="32" cy="20" r="11" fill="currentColor" opacity="0.92" />
      <path d="M14 54c2.8-9 10.2-14 18-14s15.2 5 18 14" fill="none" stroke="currentColor" strokeWidth="6" strokeLinecap="round" />
    </svg>
  )

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setErrorMessage('')
    saveStoredProfile(user.email, {
      displayName: displayName.trim() || user.fullName,
      photoDataUrl,
      sport,
      focusArea,
      dateOfBirth,
    })
    if (user.role === 'coach') {
      try {
        const updatedProfile = await updateCoachProfile({
          name: displayName.trim() || user.fullName,
          phone,
          profileImage: photoDataUrl,
          specialization,
          status: coachStatus,
        })
        setCoachProfile(updatedProfile)
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'Unable to update coach profile.')
        return
      }
    }
    setSuccessMessage(user.role === 'coach' ? 'Coach profile saved.' : 'Profile preferences saved.')
  }

  const handlePhotoChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      const result = typeof reader.result === 'string' ? reader.result : null
      setPhotoDataUrl(result)
      setSuccessMessage('')
    }
    reader.readAsDataURL(file)
  }

  return (
    <section className="profile-page-shell">
      <div className="profile-page-container">
        <div className="profile-page-hero">
          <p className="profile-page-eyebrow">Profile</p>
          <h1>Your account space</h1>
          <p>Set the profile photo and username display that appear across the application header and user menu.</p>
        </div>

        <form className="profile-page-card" onSubmit={handleSave}>
          <div className="profile-page-layout">
            <div className="profile-page-avatar-block">
              <button type="button" className="profile-page-avatar" onClick={() => fileInputRef.current?.click()}>
                {photoDataUrl ? <img src={photoDataUrl} alt={`${displayName || user.fullName} profile`} /> : renderAvatarFallback()}
              </button>
              <button type="button" className="profile-page-photo-button" onClick={() => fileInputRef.current?.click()}>
                {photoDataUrl ? 'Change photo' : 'Upload photo'}
              </button>
              {photoDataUrl ? (
                <button type="button" className="profile-page-photo-reset" onClick={() => setPhotoDataUrl(null)}>
                  Remove photo
                </button>
              ) : null}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="profile-page-file-input"
                onChange={handlePhotoChange}
              />
            </div>

            <div className="profile-page-fields">
              <label>
                <span>Username</span>
                <input
                  value={displayName}
                  onChange={(event) => {
                    setDisplayName(event.target.value)
                    setSuccessMessage('')
                  }}
                  maxLength={80}
                  placeholder="Enter your preferred username"
                />
                <small>This display name appears in the header profile area.</small>
              </label>

              <label>
                <span>Email</span>
                <input value={user.email} disabled />
                <small>Email comes from your sign-in account.</small>
              </label>

              <label>
                <span>Role</span>
                <input value={user.role === 'coach' ? 'Coach' : 'Student'} disabled />
                <small>Role is assigned from your account type.</small>
              </label>

              {user.role === 'coach' ? (
                <label>
                  <span>Coach UUID</span>
                  <input value={coachProfile?.coachId ?? 'Not mapped'} disabled />
                  <small>Dashboard assignment key from `hamsatech.coaches.coach_id`.</small>
                </label>
              ) : null}

              {user.role === 'coach' ? (
                <label>
                  <span>Phone</span>
                  <input value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="Coach phone number" />
                </label>
              ) : null}

              {user.role === 'coach' ? (
                <label>
                  <span>Specialization</span>
                  <input value={specialization} onChange={(event) => setSpecialization(event.target.value)} placeholder="Example: Shooting performance" />
                </label>
              ) : null}

              {user.role === 'coach' ? (
                <label>
                  <span>Status</span>
                  <select value={coachStatus} onChange={(event) => setCoachStatus(event.target.value as typeof coachStatus)}>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Assignment Status</span>
                  <input value={user.assignmentStatus ?? 'unassigned'} disabled />
                  <small>This updates when a coach approves your request.</small>
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Assigned Coach</span>
                  <input value={user.assignedCoachName ?? 'Not assigned'} disabled />
                  <small>Your profile and intake stay linked to this coach.</small>
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Requested Coach</span>
                  <input value={user.requestedCoachName ?? 'Not requested'} disabled />
                  <small>Pending requests appear here until the coach approves you.</small>
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Requested Coach Code</span>
                  <input value={user.requestedCoachCode ?? 'Not requested'} disabled />
                  <small>If you update your request from the dashboard, it will appear here.</small>
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Assigned Coach Code</span>
                  <input value={user.assignedCoachCode ?? 'Not assigned'} disabled />
                  <small>This appears after the coach approves your request.</small>
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Coach Email</span>
                  <input value={user.assignedCoachEmail ?? 'Not assigned'} disabled />
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Sport</span>
                  <input
                    value={sport}
                    onChange={(event) => {
                      setSport(event.target.value)
                      setSuccessMessage('')
                    }}
                    placeholder="Enter your sport"
                  />
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Focus Area</span>
                  <input
                    value={focusArea}
                    onChange={(event) => {
                      setFocusArea(event.target.value)
                      setSuccessMessage('')
                    }}
                    placeholder="Enter your focus area"
                  />
                </label>
              ) : null}

              {user.role === 'student' ? (
                <label>
                  <span>Date of Birth</span>
                  <input
                    type="date"
                    value={dateOfBirth}
                    onChange={(event) => {
                      setDateOfBirth(event.target.value)
                      setSuccessMessage('')
                    }}
                  />
                  <small>Students can update these details here after signup.</small>
                </label>
              ) : null}
            </div>
          </div>

          <div className="profile-page-actions">
            <div>
              {errorMessage ? <p className="profile-page-error">{errorMessage}</p> : null}
              {successMessage ? <p className="profile-page-success">{successMessage}</p> : null}
            </div>
            <div className="profile-page-actions-right">
              <Link to={user.role === 'coach' ? '/coach/dashboard' : '/dashboard'} className="profile-page-secondary">Back to Dashboard</Link>
              <button type="submit" className="profile-page-submit">Save Profile</button>
            </div>
          </div>
        </form>
      </div>
    </section>
  )
}

export default ProfilePage
