import { FormEvent, useMemo, useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import '../styles/Auth.css'

function SignUpPage() {
  const { user, signUp } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const from = useMemo(
    () => (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/dashboard',
    [location.state],
  )

  if (user) {
    return <Navigate to={from} replace />
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await signUp({
        fullName,
        email,
        password,
        role: 'student',
      })
      navigate('/dashboard', { replace: true })
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : 'Unable to sign up')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-card">
        <div className="auth-copy">
          <p className="auth-eyebrow">Join HamsaTech</p>
          <h1 className="auth-title">Create your student account</h1>
          <p className="auth-text">
            Student signup stays open, while coach access stays restricted. Create your account first, then request your coach assignment after sign-in so the right coach can approve access to your intake and feedback.
          </p>
          <div className="auth-heritage-panel">
            <span className="auth-heritage-mark">SECURE ASSIGNMENT FLOW</span>
            <p>
              Coaches are meant to be provisioned separately. Public signup here is intentionally limited to students so personal athlete data is never exposed across unrelated coach accounts.
            </p>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-static-role">
            <span className="auth-static-role-label">Account Type</span>
            <div className="role-card active">
              <span className="role-card-title">Student</span>
              <span className="role-card-copy">Complete your own intake, view coach observations, and track progress over time.</span>
            </div>
          </div>

          <label className="auth-field">
            <span>Full Name</span>
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} required />
          </label>

          <label className="auth-field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
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
                autoComplete="new-password"
                minLength={8}
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
                    <path
                      d="M3 3l18 18"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M10.6 10.6a3 3 0 004.2 4.2"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M6.7 6.7C4 8.5 2.2 11 2 12c.3 1.2 3.6 7 10 7 1.8 0 3.3-.4 4.6-1"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M9.8 4.2A11.5 11.5 0 0112 4c6.4 0 9.7 5.8 10 8-.1.8-1.5 3.8-4 5.8"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                    <path
                      d="M2 12c.3-2.2 3.6-8 10-8s9.7 5.8 10 8c-.3 2.2-3.6 8-10 8S2.3 14.2 2 12z"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M12 15a3 3 0 100-6 3 3 0 000 6z"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinejoin="round"
                    />
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
            {isSubmitting ? 'Creating Account...' : 'Create Account'}
          </button>

          <p className="auth-footnote">
            Already have an account? <Link to="/signin">Sign in here</Link>
          </p>
        </form>
      </div>
    </section>
  )
}

export default SignUpPage
