import { useNavigate } from 'react-router-dom'
import '../styles/About.css'
import '../styles/FeatureCard.css'
import image4 from '../images/image4.jpg'
import image5 from '../images/image5.jpg'
import image6 from '../images/image6.png'

const useCasesItems = [
  {
    id: 1,
    title: 'Athlete Performance',
    description: 'Personalized training plans based on AI analytics for athletes.',
    image: image4
  },
  {
    id: 2,
    title: 'Wellness Optimization',
    description: 'Behavioral insights to improve recovery, sleep, and mindfulness.',
    image: image5
  },
  {
    id: 3,
    title: 'Decision Intelligence',
    description: 'Data-backed decisions for coaching, career, and life strategy.',
    image: image6
  }
]

function UseCasesPage() {
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
        <h2 className="about-title">Use Cases</h2>
        <p className="about-description">
          Explore complete use-case paths designed for sports professionals,
          wellness seekers, and high performers.
        </p>

        <div className="features-grid" style={{ marginTop: '40px' }}>
          {useCasesItems.map((item) => (
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

export default UseCasesPage
