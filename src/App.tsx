import { Routes, Route } from 'react-router-dom'
import './App.css'
import Hero from './components/Hero'
import FeatureCard from './components/FeatureCard'
import Navigation from './components/Navigation'
import About from './components/About'
import AboutPage from './components/AboutPage'
import NextPage from './components/NextPage'
import PlatformPage from './components/PlatformPage'
import UseCasesPage from './components/UseCasesPage'
import HowItWorksPage from './components/HowItWorksPage'
import ScrollToHash from './components/ScrollToHash'

function App() {
  const features = [
    {
      id: 1,
      title: 'AI Coaching',
      description: 'Data-driven performance insights for athletes.'
    },
    {
      id: 2,
      title: 'Smart Analytics',
      description: 'Track, analyze, and improve every move.'
    },
    {
      id: 3,
      title: 'Elite Training',
      description: 'Olympic-level precision training systems.'
    }
  ]

  return (
    <div className="App">
      <ScrollToHash />
      <Navigation />
      <Routes>
        <Route path="/" element={<NextPage />} />
        <Route
          path="/home"
          element={
            <>
              <Hero />
              <section id="platform" className="features-section">
                <div className="container">
                  <div className="features-grid">
                    {features.map((feature) => (
                      <FeatureCard key={feature.id} {...feature} />
                    ))}
                  </div>
                </div>
              </section>
              <About />
              <section id="contact" className="about-section">
                <div className="container">
                  <h2>Contact</h2>
                  <p>Reach us at contact@hamsatech.ai</p>
                </div>
              </section>
            </>
          }
        />
        <Route path="/platform" element={<PlatformPage />} />
        <Route path="/usecases" element={<UseCasesPage />} />
        <Route path="/howitworks" element={<HowItWorksPage />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
    </div>
  )
}

export default App
