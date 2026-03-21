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
        <h1 className="hero-title">Precision. Intelligence. Performance.</h1>
        <p className="hero-subtitle">AI-powered insights for elite sports training and human excellence.</p>
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
