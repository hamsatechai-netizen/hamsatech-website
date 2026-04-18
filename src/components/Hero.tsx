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
  <>
    <section className="hero" id="home">
      <div className="hero-content">
        <h1 className="hero-title">
          Unified intelligence for better decisions and outcomes
        </h1>

        <p className="hero-subtitle">
          Combining data, behavior, and performance signals — so you can understand, act, and improve with clarity.
        </p>

        <p className="hero-micro">
          Most performance challenges aren’t visible — until they impact outcomes.
        </p>
      </div>
    </section>

    <section className="problem-section">
      <div className="container">
        <h2 className="section-title">
          Performance isn’t limited by effort — it’s limited by visibility
        </h2>

        <div className="problem-grid">
          <div className="problem-card">
            <h3>Disconnected Data</h3>
            <p>
              Data exists across devices and experiences, but it remains scattered and hard to connect.
            </p>
          </div>

          <div className="problem-card">
            <h3>Unseen Influences</h3>
            <p>
              Stress, emotions, and behavior impact outcomes — yet they are rarely understood or measured.
            </p>
          </div>

          <div className="problem-card">
            <h3>Unclear Decisions</h3>
            <p>
              Even with data, knowing what to change, when, and why is unclear — leading to inconsistent progress.
            </p>
          </div>
        </div>
      </div>
    </section>
  </>
);

export default Hero
