import { useNavigate } from 'react-router-dom'
import '../styles/About.css'
import '../styles/FeatureCard.css'
import image1 from '../images/image1.jpg'
import image2 from '../images/image2.jpg'
import image4 from '../images/image4.jpg'
import image5 from '../images/image5.jpg'
import image6 from '../images/image6.png'

const useCasesItems = [
  {
    id: 1,
    title: 'Athlete Mental Wellness',
    description: 'Precision performance for shooters and young athletes — combining heart rate, HRV, movement analysis, and psychology to decode what\'s holding performance back.',
    image: image4
  },
  {
    id: 2,
    title: 'Student Stress & Focus',
    description: 'Every hour, a student in India faces crisis from academic pressure (NCRB 2023). HamsaTech provides early detection, emotional guidance, and focus tools for students and their families.',
    image: image5
  },
  {
    id: 3,
    title: 'Pre-Marriage Compatibility',
    description: 'AI-powered emotional and psychological compatibility insights — helping couples understand communication patterns, emotional disconnect, and shared values before committing for life.',
    image: image6
  },
  {
    id: 4,
    title: 'Employee Wellness',
    description: '70% of employees in India experience stress that impacts productivity and health. HamsaTech detects burnout early and delivers personalized recovery plans for individuals and teams.',
    image: image1
  },
  {
    id: 5,
    title: "Women's Health & Wellness",
    description: 'Women balance 3–5 roles with little emotional support. HamsaTech offers holistic wellness — tracking physical, emotional, and social wellbeing across every stage of life.',
    image: image2
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
          Five modules. One mission: heal the human mind through empathy and AI.
          From the shooting range to the classroom, from relationships to the workplace — HamsaTech meets you where life is hardest.
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
