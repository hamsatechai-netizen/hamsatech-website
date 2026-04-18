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

  const goToAbout = () => {
    navigate('/about')
  }

  return (
    <section className="hero" id="home">
      <div className="hero-content">
        <h1 className="hero-title">Unified intelligence for better decisions and outcomes</h1>
        <p className="hero-subtitle">Combining data, behavior, and performance signals — so you can understand, act, and improve with clarity</p>
        <div className="hero-buttons">
          <button className="btn btn-primary" onClick={goToPlatform}>Platform</button>
          <button className="btn btn-primary" onClick={goToUseCases}>Use Cases</button>
          <button className="btn btn-primary" onClick={goToHowItWorks}>How It Works</button>
          <button className="btn btn-primary" onClick={goToAbout}>About</button>
        </div>
      </div>
    </section>
  )
}

export default Hero
