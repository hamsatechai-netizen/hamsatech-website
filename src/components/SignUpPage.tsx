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
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="new-password"
              minLength={8}
              required
            />
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
