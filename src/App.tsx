import { Suspense, lazy, useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import AppSplash from './components/AppSplash'
import Navigation from './components/Navigation'
import ScrollNavigator from './components/ScrollNavigator'
import Footer from './components/Footer'
import PageLoader from './components/PageLoader'
import SaarthiBot from './components/SaarthiBot'
import { useAuth } from './context/AuthContext'

const HomePage = lazy(() => import('./components/HomePage'))
const AboutPage = lazy(() => import('./components/AboutPage'))
const PlatformPage = lazy(() => import('./components/PlatformPage'))
const UseCasesPage = lazy(() => import('./components/UseCasesPage'))
const HowItWorksPage = lazy(() => import('./components/HowItWorksPage'))
const SignOutPage = lazy(() => import('./components/SignOutPage'))
const CoachAthleteDetailsPage = lazy(() => import('./components/CoachAthleteDetailsPage'))
const CoachLoginPage = lazy(() => import('./components/CoachLoginPage'))
const CoachDashboardPage = lazy(() => import('./components/coach/CoachDashboardV1Page'))
const CoachFeedbackRequestPage = lazy(() => import('./components/coach/CoachFeedbackRequestPage'))
const PendingAssignmentsPage = lazy(() => import('./components/coach/PendingAssignmentsPage'))
const ProfilePage = lazy(() => import('./components/ProfilePage'))

function DashboardRoute() {
  const { user, isLoading } = useAuth()

  if (!isLoading && user?.role === 'coach') {
    return <Navigate to="/coach/dashboard" replace />
  }

  if (!isLoading) {
    return <Navigate to="/coach/login" replace />
  }

  return <PageLoader />
}

function App() {
  const [isBooting, setIsBooting] = useState(true)

  useEffect(() => {
    let cancelled = false
    const startedAt = Date.now()
    const minSplashMs = 450
    const maxSplashMs = 2500

    const logoReady = new Promise<void>((resolve) => {
      const img = new Image()
      img.onload = () => resolve()
      img.onerror = () => resolve()
      img.src = '/logo-mark-white-384.png'
    })

    const homeChunkReady = import('./components/HomePage')

    const hardTimeout = window.setTimeout(() => {
      if (!cancelled) {
        setIsBooting(false)
      }
    }, maxSplashMs)

    Promise.allSettled([logoReady, homeChunkReady]).then(() => {
      window.clearTimeout(hardTimeout)
      const elapsed = Date.now() - startedAt
      const remaining = Math.max(0, minSplashMs - elapsed)
      window.setTimeout(() => {
        if (!cancelled) {
          setIsBooting(false)
        }
      }, remaining)
    })

    return () => {
      cancelled = true
      window.clearTimeout(hardTimeout)
    }
  }, [])

  if (isBooting) {
    return <AppSplash />
  }

  return (
    <div className="App">
      <ScrollNavigator />
      <Navigation />
      <main className="app-main">
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/home" element={<Navigate to="/" replace />} />
            <Route path="/platform" element={<PlatformPage />} />
            <Route path="/usecases" element={<UseCasesPage />} />
            <Route path="/howitworks" element={<HowItWorksPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/signin" element={<CoachLoginPage />} />
            <Route path="/signup" element={<Navigate to="/coach/login" replace />} />
            <Route path="/signout" element={<SignOutPage />} />
            <Route path="/dashboard" element={<DashboardRoute />} />
            <Route path="/coach/login" element={<CoachLoginPage />} />
            <Route path="/coach/dashboard" element={<CoachDashboardPage />} />
            <Route path="/coach/feedback/new" element={<CoachFeedbackRequestPage />} />
            <Route path="/coach/assignments/pending" element={<PendingAssignmentsPage />} />
            <Route path="/coach/athletes/:athleteId" element={<CoachAthleteDetailsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
      <SaarthiBot />
    </div>
  )
}

export default App
