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
        <button
          onClick={goBack}
          style={{
            border: 'none',
            background: 'transparent',
            color: '#021d39',
            fontSize: '1.4rem',
            marginBottom: '20px',
            cursor: 'pointer'
          }}
          aria-label="Go back"
        >
          ← Back
        </button>
        <h2 className="about-title">How It Works</h2>
        <p className="about-description">
          A simplified, compelling execution path to start using HamsaTech right away.
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
      <div className="how-it-works-bottom" style={{ background: '#021d39', color: '#fff', textAlign: 'center', padding: '80px 20px' }}>
        <h2 style={{ fontSize: '3rem', marginBottom: '20px' }}>Start Building Your Personal Intelligence</h2>
        <p style={{ fontSize: '1.2rem', marginBottom: '35px' }}>Use human-centered AI to drive measurable growth in sports, wellness, and life decisions.</p>
        <button
          className="btn btn-primary"
          onClick={handleStart}
          style={{ backgroundColor: '#ffd700', color: '#000', border: 'none', padding: '16px 34px', fontSize: '1.1rem' }}
        >
          Get Started
        </button>
      </div>
    </section>
  )
}

export default HowItWorksPage
