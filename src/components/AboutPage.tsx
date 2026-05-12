import { useNavigate } from 'react-router-dom'
import '../styles/About.css'

function AboutPage() {
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
        <h2 className="about-title">About HamsaTech</h2>

        <h3 className="about-section-heading">Our Purpose</h3>
        <p className="about-description">
          Healing the human mind through empathy and AI. At HamsaTech.ai, we create AI-driven companions
          that guide, calm, and uplift individuals — helping them navigate stress, relationships, and
          identity with emotional intelligence and mindfulness.
        </p>

        <h3 className="about-section-heading">Our Vision</h3>
        <p className="about-description">
          To make technology a catalyst for emotional awakening and social harmony.<br />
          <em>"Technology that heals, connects, and awakens."</em>
        </p>

        <h3 className="about-section-heading">Our Framework</h3>
        <p className="about-description">
          <strong>Spiritual Intelligence:</strong> Inspired by the Bhagavad Gita, yoga, and mindfulness
          practices — a "Pocket Gita" that senses a user's emotional pulse and offers contextual reflections.
        </p>
        <p className="about-description">
          <strong>Psychological Intelligence:</strong> Co-created with sports psychologists and behavioral
          experts to translate spiritual wisdom into daily self-regulation habits and measurable growth.
        </p>

        <h3 className="about-section-heading">The Founder</h3>
        <p className="about-description">
          <strong>Anita Ayyagari</strong> — Technologist with Empathy. Seeker with Purpose.
        </p>
        <p className="about-description">
          15+ years in Data, AI &amp; Cloud Architecture at Informatica. M.Tech in AI/ML + Leadership in AI from ISB.
          Passionate about merging empathy with innovation to solve real human problems.
        </p>
        <p className="about-description" style={{ fontStyle: 'italic', fontWeight: 600 }}>
          "When AI learns to feel, humanity learns to heal."
        </p>
      </div>
    </section>
  )
}

export default AboutPage
