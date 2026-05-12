import { useNavigate } from 'react-router-dom'
import '../styles/About.css'
import '../styles/FeatureCard.css'

const howItWorksItems = [
  {
    id: 1,
    title: 'We Listen to You',
    description: 'A psychology assessment, biometric sensors (Polar H10), and daily check-ins capture the full picture — your emotional state, your body\'s signals, and your performance data.'
  },
  {
    id: 2,
    title: 'We Understand You',
    description: 'AI triangulates psychology, biometrics, and performance to surface root causes — not surface symptoms. Deterministic scoring. No guesswork.'
  },
  {
    id: 3,
    title: 'We Help You Grow',
    description: 'Personalized, culturally-grounded guidance delivered to athletes, coaches, parents, students, and professionals — in language that heals and empowers.'
  }
]

function HowItWorksPage() {
  const navigate = useNavigate()

  const handleStart = () => {
    navigate('/signup')
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
          {'<-'} Back
        </button>
        <h2 className="about-title">How It Works</h2>
        <p className="about-description">
          Three steps. One continuous loop of empathy, intelligence, and growth.
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
      <div
        className="how-it-works-bottom"
        style={{ background: '#021d39', color: '#fff', textAlign: 'center', padding: '80px 20px' }}
      >
        <h2 style={{ fontSize: '3rem', marginBottom: '20px' }}>
          Ready to begin your journey?
        </h2>
        <p style={{ fontSize: '1.2rem', marginBottom: '35px' }}>
          Join HamsaTech and let AI-powered empathy guide you toward clarity, calm, and peak performance.
        </p>
        <button
          className="btn btn-primary"
          onClick={handleStart}
          style={{ backgroundColor: '#ffd700', color: '#000', border: 'none', padding: '16px 34px', fontSize: '1.1rem' }}
        >
          Get Started — It's Free
        </button>
      </div>
    </section>
  )
}

export default HowItWorksPage
