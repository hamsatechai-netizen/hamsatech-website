import { useNavigate } from 'react-router-dom'
import '../styles/About.css'
import '../styles/FeatureCard.css'
import image1 from '../images/image1.jpg'
import image2 from '../images/image2.jpg'
import image3 from '../images/image3.png'

const platformItems = [
  {
    id: 1,
    title: 'Psychology Assessment',
    description: 'Structured questionnaires co-designed with behavioral experts to map emotional patterns, stress triggers, arousal levels, and identity across every life domain.',
    image: image1
  },
  {
    id: 2,
    title: 'Biometric Intelligence',
    description: 'Real-time heart rate, HRV (RMSSD), and movement analysis from Polar H10 — revealing what your body is doing beneath the surface during performance and recovery.',
    image: image2
  },
  {
    id: 3,
    title: 'AI Insight Engine',
    description: 'Deterministic scoring — stability, fatigue, stress, recovery — combined with empathetic AI that converts structured findings into athlete-friendly, coach-friendly, and parent-friendly language.',
    image: image3
  }
]

function PlatformPage() {
  const navigate = useNavigate()

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
        <h2 className="about-title">The Platform</h2>
        <p className="about-description">
          HamsaTech triangulates three intelligence layers — Psychology, Biometrics, and Performance — to
          build a complete picture of who you are and what you need. Not a generic dashboard. A personal
          intelligence system built around you.
        </p>
        <div className="features-grid" style={{ marginTop: '40px' }}>
          {platformItems.map((item) => (
            <div key={item.id} className="feature-card" style={{ padding: '0', overflow: 'hidden' }}>
              <img src={item.image} alt={item.title} style={{ width: '100%', height: '220px', objectFit: 'cover' }} />
              <div style={{ padding: '20px' }}>
                <h3 className="feature-title">{item.title}</h3>
                <p className="feature-description">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PlatformPage
