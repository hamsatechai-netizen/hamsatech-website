import { useEffect, useRef, useState, type ChangeEvent } from 'react'
import { Link, NavLink } from 'react-router-dom'
import '../styles/Navigation.css'
import { useAuth } from '../context/AuthContext'
import { getStoredProfile, saveStoredProfile, subscribeToStoredProfile } from '../lib/profileStorage'

function Navigation() {
  const [isOpen, setIsOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [profileImage, setProfileImage] = useState<string | null>(null)
  const [displayName, setDisplayName] = useState('')
  const [profileSport, setProfileSport] = useState('')
  const { user, isLoading } = useAuth()
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const profileMenuRef = useRef<HTMLDivElement | null>(null)
  const closeMenu = () => setIsOpen(false)

  useEffect(() => {
    if (!user?.email) {
      setProfileImage(null)
      setDisplayName('')
      setProfileSport('')
      return
    }

    const syncProfile = () => {
      const storedProfile = getStoredProfile(user.email)
      setProfileImage(storedProfile.photoDataUrl ?? null)
      setDisplayName(storedProfile.displayName?.trim() || user.fullName)
      setProfileSport(storedProfile.sport ?? user.sport ?? '')
    }

    syncProfile()
    return subscribeToStoredProfile((email) => {
      if (!email || email === user.email.toLowerCase()) {
        syncProfile()
      }
    })
  }, [user?.email, user?.fullName, user?.sport])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (!profileMenuRef.current?.contains(event.target as Node)) {
        setIsProfileOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const openPhotoPicker = () => {
    fileInputRef.current?.click()
  }

  const renderAvatarFallback = () => (
    <svg viewBox="0 0 64 64" aria-hidden="true" className="profile-avatar-icon">
      <circle cx="32" cy="20" r="11" fill="currentColor" opacity="0.92" />
      <path d="M14 54c2.8-9 10.2-14 18-14s15.2 5 18 14" fill="none" stroke="currentColor" strokeWidth="6" strokeLinecap="round" />
    </svg>
  )

  const handlePhotoChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file || !user?.email) {
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      const result = typeof reader.result === 'string' ? reader.result : null
      if (!result) {
        return
      }

      saveStoredProfile(user.email, {
        ...getStoredProfile(user.email),
        photoDataUrl: result,
        displayName: displayName || user.fullName,
      })
      setProfileImage(result)
    }
    reader.readAsDataURL(file)
  }

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          <span className="logo-icon" aria-hidden="true">
            <img
              src="/logo-mark-128.png"
              srcSet="/logo-mark-128.png 1x, /logo-mark-256.png 2x, /logo-mark-384.png 3x"
              sizes="40px"
              alt="HamsaTech"
              decoding="async"
            />
          </span>
          <span className="logo-text">HamsaTech</span>
        </Link>
        
        <button
          className={`menu-toggle ${isOpen ? 'active' : ''}`}
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle navigation menu"
          aria-expanded={isOpen}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <ul className={`nav-menu ${isOpen ? 'active' : ''}`}>
          <li>
            <NavLink to="/" onClick={closeMenu}>
              Home
            </NavLink>
          </li>
          <li>
            <NavLink to="/home#contact" onClick={closeMenu}>
              Contact
            </NavLink>
          </li>
          {user ? (
            <li>
              <NavLink to="/dashboard" onClick={closeMenu}>
                Dashboard
              </NavLink>
            </li>
          ) : null}
          {user ? (
            <li>
              <NavLink to="/athlete-intake" onClick={closeMenu}>
                {user.role === 'coach' ? 'Intake' : 'My Intake'}
              </NavLink>
            </li>
          ) : null}
        </ul>

        <div className="nav-auth">
          {isLoading ? (
            <span className="auth-loading">Loading...</span>
          ) : user ? (
            <div className="profile-menu" ref={profileMenuRef}>
              <button
                type="button"
                className="profile-trigger"
                onClick={() => setIsProfileOpen((current) => !current)}
                aria-expanded={isProfileOpen}
                aria-label="Open profile menu"
              >
                <span className="profile-avatar">
                  {profileImage ? <img src={profileImage} alt={`${user.fullName} profile`} /> : renderAvatarFallback()}
                </span>
                <span className="profile-name">{displayName || user.fullName}</span>
              </button>

              {isProfileOpen ? (
                <div className="profile-dropdown">
                  <div className="profile-dropdown-header">
                    <button type="button" className="profile-avatar profile-avatar-large" onClick={openPhotoPicker}>
                      {profileImage ? <img src={profileImage} alt={`${user.fullName} profile`} /> : renderAvatarFallback()}
                    </button>
                    <div>
                      <p className="profile-role">{user.role === 'coach' ? 'Coach' : 'Student'}</p>
                      <h3>{displayName || user.fullName}</h3>
                      <p className="profile-email">{user.email}</p>
                    </div>
                  </div>

                  <dl className="profile-details">
                    <div>
                      <dt>Username</dt>
                      <dd>{displayName || user.fullName}</dd>
                    </div>
                    <div>
                      <dt>Role</dt>
                      <dd>{user.role === 'coach' ? 'Coach' : 'Student'}</dd>
                    </div>
                    {profileSport ? (
                      <div>
                        <dt>Sport</dt>
                        <dd>{profileSport}</dd>
                      </div>
                    ) : null}
                  </dl>

                  <button type="button" className="profile-photo-link" onClick={openPhotoPicker}>
                    Set profile photo
                  </button>
                  <NavLink to="/profile" className="profile-link-card" onClick={() => setIsProfileOpen(false)}>
                    View profile
                  </NavLink>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="profile-file-input"
                    onChange={handlePhotoChange}
                  />

                  <NavLink to="/signout" className="logout-btn profile-logout" onClick={closeMenu}>
                    Sign Out
                  </NavLink>
                </div>
              ) : null}
            </div>
          ) : (
            <>
              <NavLink
                to="/signup"
                className={({ isActive }) => `auth-btn ${isActive ? 'auth-btn--primary' : 'auth-btn--secondary'}`}
                onClick={closeMenu}
              >
                Sign Up
              </NavLink>
              <NavLink
                to="/signin"
                className={({ isActive }) => `auth-btn ${isActive ? 'auth-btn--primary' : 'auth-btn--secondary'}`}
                onClick={closeMenu}
              >
                Sign In
              </NavLink>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navigation
