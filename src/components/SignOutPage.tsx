import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import '../styles/Auth.css'

function SignOutPage() {
  const { user, signOut } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(true)
  const [hasSignedOut, setHasSignedOut] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const performSignOut = async () => {
      try {
        await signOut()
        setHasSignedOut(true)
      } catch (signOutError) {
        setError(signOutError instanceof Error ? signOutError.message : 'Unable to sign out')
      } finally {
        setIsSubmitting(false)
      }
    }

    if (user) {
      void performSignOut()
    } else {
      setIsSubmitting(false)
    }
  }, [signOut, user])

  if (!user && !isSubmitting && !error && !hasSignedOut) {
    return <Navigate to="/signin" replace />
  }

  return (
    <section className="auth-shell auth-shell-signout">
      <div className="auth-card auth-card-compact">
        <p className="auth-eyebrow">Session Update</p>
        <h1 className="auth-title">{isSubmitting ? 'Signing you out...' : 'You are signed out'}</h1>
        <p className="auth-text">
          {error
            ? error
            : 'Your authenticated session has been cleared. You can sign back in whenever you are ready.'}
        </p>
        <div className="auth-actions">
          <Link className="auth-submit auth-link-button" to="/signin">
            Sign In Again
          </Link>
          <Link className="auth-secondary-link" to="/">
            Return to Home
          </Link>
        </div>
      </div>
    </section>
  )
}

export default SignOutPage
