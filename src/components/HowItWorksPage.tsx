import { useNavigate } from 'react-router-dom'
import '../styles/About.css'
import '../styles/FeatureCard.css'

const howItWorksItems = [
  {
    id: 1,
    title: 'Understand You',
    description: 'Collect performance and behavior data to create a personalized intelligence profile.'
  },
  {
    id: 2,
    title: 'Guide You',
    description: 'Recommend training, wellness, and decision actions that align with your goals.'
  },
  {
    id: 3,
    title: 'Measure Growth',
    description: 'Track progress with data-driven metrics and continuous feedback loops.'
  }
]

function HowItWorksPage() {
  const navigate = useNavigate()

  const handleStart = () => {
    navigate('/')
  }

  const goBack = () => {
    navigate(-1)
  }

  return (
    <section className="about-section">
      <div className="container">
        <button onClick={goBack} className="page-return-button" aria-label="Go back">
          <span className="page-return-button-icon" aria-hidden="true">&larr;</span>
          <span>Return to Overview</span>
        </button>
        <h2 className="about-title">How It Works</h2>
        <p className="about-description">
          A simplified, compelling execution path to start using HamsaTech right
          away.
        </p>
        <div className="features-grid" style={{ marginTop: '40px' }}>
          {howItWorksItems.map((item) => (
            <div key={item.id} className="feature-card">
              <h3 className="feature-title">{item.title}</h3>
              <p className="feature-description">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="how-it-works-bottom">
        <h2 className="how-it-works-bottom-title">Start Building Your Personal Intelligence</h2>
        <p className="how-it-works-bottom-text">
          Use human-centered AI to drive measurable growth in sports, wellness,
          and life decisions.
        </p>
        <button className="how-it-works-bottom-button" onClick={handleStart}>
          Get Started
        </button>
      </div>
    </section>
  )
}

export default HowItWorksPage
