import '../styles/About.css'
import '../styles/FeatureCard.css'
import image1 from '../images/image1.jpg'
import image2 from '../images/image2.jpg'
import image3 from '../images/image3.png'

const platformItems = [
  {
    id: 1,
    title: 'Performance Optimization',
    description: 'Improve how you train, recover, and perform.',
    image: image1,
  },
  {
    id: 2,
    title: 'Self-Discovery',
    description: 'Understand your patterns, strengths, and blind spots.',
    image: image2,
  },
  {
    id: 3,
    title: 'Data-Driven Guidance',
    description: 'Make better decisions in sports, wellness, and life.',
    image: image3,
  },
]

function PlatformPage() {
  return (
    <section className="about-section">
      <div className="container">
        <h2 className="about-title">A unified intelligence platform that understands you — and guides better decisions</h2>
        <p className="about-description">
         HamsaTech brings together data, behavior, and context into a continuous system — helping you understand what’s happening, 
          make better decisions, and improve over time.
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

