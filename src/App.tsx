import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import Navigation from './components/Navigation'
import ScrollNavigator from './components/ScrollNavigator'
import Footer from './components/Footer'
import PageLoader from './components/PageLoader'

const HomePage = lazy(() => import('./components/HomePage'))
const AboutPage = lazy(() => import('./components/AboutPage'))
const PlatformPage = lazy(() => import('./components/PlatformPage'))
const UseCasesPage = lazy(() => import('./components/UseCasesPage'))
const HowItWorksPage = lazy(() => import('./components/HowItWorksPage'))
const SignInPage = lazy(() => import('./components/SignInPage'))
const SignUpPage = lazy(() => import('./components/SignUpPage'))
const SignOutPage = lazy(() => import('./components/SignOutPage'))
const DashboardPage = lazy(() => import('./components/DashboardPage'))
const AthleteIntakePage = lazy(() => import('./components/AthleteIntakePage'))
const CoachAthleteDetailsPage = lazy(() => import('./components/CoachAthleteDetailsPage'))
const ProfilePage = lazy(() => import('./components/ProfilePage'))

function App() {
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
            <Route path="/signin" element={<SignInPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/signout" element={<SignOutPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/athlete-intake" element={<AthleteIntakePage />} />
            <Route path="/coach/athletes/:athleteId" element={<CoachAthleteDetailsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
    </div>
  )
}

export default App
