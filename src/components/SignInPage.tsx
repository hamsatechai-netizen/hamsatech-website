import { FormEvent, useMemo, useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import '../styles/Auth.css'

function SignInPage() {
  const { user, signIn } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
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
      await signIn(email, password)
      navigate(from, { replace: true })
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : 'Unable to sign in')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-card">
        <div className="auth-copy">
          <p className="auth-eyebrow">Secure Access</p>
          <h1 className="auth-title">Sign in to your HamsaTech workspace</h1>
          <p className="auth-text">
            Access your AI-guided platform experience with the same precision and clarity
            as the rest of the site.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="name@hamsatech.ai"
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
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />
          </label>

          {error ? (
            <p className="auth-message auth-error" role="alert" aria-live="polite">
              {error}
            </p>
          ) : null}

          <button className="auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing In...' : 'Sign In'}
          </button>

          <p className="auth-footnote">
            Returning to the site without signing in? <Link to="/home">Go back to Home</Link>
          </p>
          <p className="auth-footnote">
            Need a new account? <Link to="/signup">Create one</Link>
          </p>
        </form>
      </div>
    </section>
  )
}

export default SignInPage
