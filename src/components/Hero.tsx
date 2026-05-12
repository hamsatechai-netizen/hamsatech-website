import { useNavigate } from 'react-router-dom'
import '../styles/Hero.css'

function Hero() {
  const navigate = useNavigate()

  const goToPlatform = () => {
    navigate('/platform')
  }

  const goToUseCases = () => {
    navigate('/usecases')
  }

  const goToHowItWorks = () => {
    navigate('/howitworks')
  }

  return (
    <section className="hero" id="home">
      <div className="hero-content">
        <h1 className="hero-title">Where Empathy Meets Innovation</h1>
        <p className="hero-subtitle">AI-driven companions that guide, calm, and uplift — helping India's athletes, students, couples, and professionals navigate stress with emotional intelligence and mindfulness.</p>
        <div className="hero-buttons">
          <button className="btn btn-primary" onClick={() => navigate('/signup')}>Get Started</button>
          <button className="btn btn-secondary" onClick={goToPlatform}>Explore Platform</button>
          <button className="btn btn-secondary" onClick={goToUseCases}>Use Cases</button>
          <button className="btn btn-secondary" onClick={goToHowItWorks}>How It Works</button>
        </div>
      </div>
    </section>
  )
}

export default Hero
