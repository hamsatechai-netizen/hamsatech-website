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
          ← Back
        </button>
        <h2 className="about-title">About HamsaTech</h2>
        <p className="about-description">
          HamsaTech is built on the belief that personal intelligence combined with AI creates transformative outcomes.
          We blend cutting-edge intelligence with human insight to drive performance gains and life improvements.
        </p>
        <p className="about-description">
          Our mission is to empower athletes, wellness seekers, and professionals with actionable data and guided growth.
          We help people see clear progress through personalized analytics, coaching, and decision support.
        </p>
      </div>
    </section>
  )
}

export default AboutPage
