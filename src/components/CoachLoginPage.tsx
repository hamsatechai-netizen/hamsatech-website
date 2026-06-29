import { FormEvent, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import '../styles/Auth.css'

function CoachLoginPage() {
  const { user, isLoading, signIn, signOut } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  if (!isLoading && user?.role === 'coach') {
    return <Navigate to="/coach/dashboard" replace />
  }

  if (!isLoading && user?.role === 'student') {
    return (
      <section className="auth-shell">
        <div className="auth-card auth-card-compact">
          <p className="auth-eyebrow">Coach Access Only</p>
          <h1 className="auth-title">This website dashboard is for coaches.</h1>
          <p className="auth-text">
            Athlete actions are handled in the app. Sign out here, then use a coach account to view athlete records on the website.
          </p>
          <div className="auth-actions">
            <button type="button" className="auth-submit" onClick={() => void signOut()}>
              Sign Out
            </button>
            <Link className="auth-secondary-link" to="/">
              Return to Home
            </Link>
          </div>
        </div>
      </section>
    )
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const signedInUser = await signIn(email, password)
      if (signedInUser.role !== 'coach') {
        await signOut()
        setError('This login is for coaches only. Students sign in at the regular sign-in page.')
        setIsSubmitting(false)
        return
      }
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : 'Unable to sign in')
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-card">
        <div className="auth-copy">
          <p className="auth-eyebrow">Coach Access</p>
          <h1 className="auth-title">Sign in to your Coach Dashboard</h1>
          <p className="auth-text">
            Review athlete progress, team performance, and app-submitted profile data in one coach-only view.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="coach@hamsatech.ai"
              autoComplete="email"
              required
            />
          </label>

          <label className="auth-field">
            <span>Password</span>
            <div className="auth-password-wrap">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="auth-password-toggle"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                aria-pressed={showPassword}
                onClick={() => setShowPassword((current) => !current)}
              >
                {showPassword ? (
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                    <path d="M3 3l18 18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M10.6 10.6a3 3 0 004.2 4.2" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M6.7 6.7C4 8.5 2.2 11 2 12c.3 1.2 3.6 7 10 7 1.8 0 3.3-.4 4.6-1" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M9.8 4.2A11.5 11.5 0 0112 4c6.4 0 9.7 5.8 10 8-.1.8-1.5 3.8-4 5.8" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                    <path d="M2 12c.3-2.2 3.6-8 10-8s9.7 5.8 10 8c-.3 2.2-3.6 8-10 8S2.3 14.2 2 12z" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                  </svg>
                )}
              </button>
            </div>
          </label>

          {error ? (
            <p className="auth-message auth-error" role="alert" aria-live="polite">
              {error}
            </p>
          ) : null}

          <button className="auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing In...' : 'Sign In as Coach'}
          </button>

          <p className="auth-footnote">
            Back to site? <Link to="/">Go to Home</Link>
          </p>
        </form>
      </div>
    </section>
  )
}

export default CoachLoginPage
