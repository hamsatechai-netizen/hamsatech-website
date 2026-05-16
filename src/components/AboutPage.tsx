import '../styles/About.css'

function AboutPage() {
  return (
    <section className="about-section">
  <div className="container">
    <h2 className="about-title">About HamsaTech</h2>
    <p className="about-description">
      HamsaTech unifies AI and human insight to create actionable intelligence—helping you understand what drives performance, relationships, and well-being.
    </p>

    <div className="philosophy-grid">
      <div className="philosophy-card">
        <h3>Our Philosophy</h3>
        <p>AI-driven companions that understand emotions through language and behavior—helping you navigate stress, relationships, and performance with clarity.</p>
      </div>

      <div className="philosophy-card">
        <h3>Vision</h3>
        <p>To make technology a catalyst for emotional awakening and social harmony.</p>
      </div>

      <div className="philosophy-card">
        <h3>Mission</h3>
        <p>Building technology that listens, heals, and empowers.</p>
      </div>
    </div>
  </div>
</section>
  )
}

export default AboutPage
