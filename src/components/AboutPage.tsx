// src/pages/About.jsx

import '../styles/About.css'

function AboutPage() {
  return (
    <div className="about-page">
      
      {/* Hero Section */}
      <section className="about-hero">
        <div className="container">
          <h1>About HamsaTech</h1>
          <p className="about-intro">
            We triangulate psychology, biosignals, and performance data—enhanced by music therapy and spiritual wisdom—into emotional intelligence you can act on.
          </p>
        </div>
      </section>

      {/* Astra Introduction */}
      <section className="astra-section">
        <div className="container">
          <div className="astra-content">
            <h2>Meet Astra</h2>
            <p>
              <strong>Astra</strong> is our flagship app—starting with elite shooting sports, expanding to parenting, relationships, and student wellness.
            </p>
          </div>
        </div>
      </section>

      {/* Philosophy, Vision, Mission Cards */}
      <section className="values-section">
        <div className="container">
          
          <div className="values-grid">
            
            <div className="value-card">
              <h3>Our Philosophy</h3>
              <p>We build AI that understands emotions—not just data—to help you navigate what matters most.</p>
            </div>

            <div className="value-card">
              <h3>Vision</h3>
              <p>To make technology a catalyst for emotional awakening and social harmony.</p>
            </div>

            <div className="value-card">
              <h3>Mission</h3>
              <p>Building technology that listens, heals, and empowers.</p>
            </div>

          </div>

        </div>
      </section>

      {/* Team Section (Optional) */}
      <section className="team-section">
        <div className="container">
          <h2 className="section-title">Built by people who care</h2>
          <p className="team-description">
            HamsaTech was founded by technologists, sports scientists, and psychologists who believe that understanding your inner state is the foundation of peak performance and lasting well-being.
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="about-cta-section">
        <div className="container">
          <h2>Ready to start your journey?</h2>
          <button className="cta-large">Get Early Access to Astra</button>
        </div>
      </section>

    </div>
  )
}

export default AboutPage
