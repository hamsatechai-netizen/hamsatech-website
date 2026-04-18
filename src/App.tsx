import { Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import Hero from './components/Hero'
import FeatureCard from './components/FeatureCard'
import Navigation from './components/Navigation'
import AboutPage from './components/AboutPage'
import PlatformPage from './components/PlatformPage'
import UseCasesPage from './components/UseCasesPage'
import HowItWorksPage from './components/HowItWorksPage'
import ScrollNavigator from './components/ScrollNavigator'
import SignInPage from './components/SignInPage'
import SignOutPage from './components/SignOutPage'
import SignUpPage from './components/SignUpPage'
import DashboardPage from './components/DashboardPage'
import AthleteIntakePage from './components/AthleteIntakePage'
import CoachAthleteDetailsPage from './components/CoachAthleteDetailsPage'
import ProfilePage from './components/ProfilePage'

function App() {
  const features = [
    {
      id: 1,
      title: 'Inner Awareness',
      description: 'Make your internal state visible — understand what your body, behavior, and emotions are really telling you.'
    },
    {
      id: 2,
      title: 'Meaningful Interpretation',
      description: 'Decode patterns across signals to identify root causes — whether it’s stress, habits, or emotional imbalance.'
    },
    {
      id: 3,
      title: 'Guided with Empathy',
      description: 'Turn insights into meaningful action with guidance that understands your context — helping you improve performance, relationships, and everyday decisions.'
    }
  ]

  return (
    <div className="App">
      <ScrollNavigator />
      <Navigation />
      <Routes>
        <Route
          path="/"
          element={
            <>
              <Hero />
              <section className="solution-section">
      <div className="container">
        <h2 className="section-title">
          A unified approach to understanding and improving performance
        </h2>
        <p className="section-subtext">
          HamsaTech connects data, behavior, and performance into a continuous feedback system — helping you see clearly, act decisively, and improve consistently.
        </p>
      </div>
    </section>
              <section id="platform" className="features-section">
                <div className="container">
                  <div className="features-grid">
                    {features.map((feature) => (
                      <FeatureCard key={feature.id} {...feature} />
                    ))}
                  </div>
                </div>
              </section>
              <section id="contact" className="about-section">
                <div className="container">
                  <h2 className="about-title">Contact</h2>
                  <p className="about-description">Reach us at contact@hamsatech.ai</p>
                </div>
              </section>
            </>
          }
        />
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
    </div>
  )
}

export default App
