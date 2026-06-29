import { Link } from 'react-router-dom'
import '../styles/Platform.css'

function PlatformPage() {
  return (
    <div className="platform-page">
      <section className="platform-hero">
        <div className="container">
          <h1>The platform that sees what you can't</h1>
          <p className="hero-subtitle">
            Astra triangulates psychology, biosignals, and performance - giving you the full picture of what's driving your outcomes.
          </p>
        </div>
      </section>

      <section className="triangulation-section">
        <div className="container">
          <h2 className="section-title">Three sources of truth, one clear picture</h2>

          <div className="triangulation-grid">
            <div className="tri-card">
              <div className="tri-icon">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="35" fill="#E8F2FF" stroke="#4F89D8" strokeWidth="2" />
                  <path d="M 30 35 Q 30 25 35 25 Q 38 25 38 28 Q 41 25 44 27 Q 46 29 45 35 Q 48 36 47 40 Q 46 43 43 43 Q 42 46 38 46 Q 34 46 32 44 Q 28 42 28 38 Q 27 35 30 35 Z" fill="#4F89D8" opacity="0.8" />
                </svg>
              </div>
              <h3>Know your patterns</h3>
              <p>
                Complete validated assessments that reveal your psychological baseline - stress response, focus tendencies, emotional patterns, decision-making style. This is who you are.
              </p>
            </div>

            <div className="tri-card">
              <div className="tri-icon">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="35" fill="#FFE8F0" stroke="#FF6B8A" strokeWidth="2" />
                  <path d="M 40 30 Q 40 25 45 25 Q 50 25 50 30 Q 50 35 40 45 Q 30 35 30 30 Q 30 25 35 25 Q 40 25 40 30" fill="#FF6B8A" opacity="0.8" />
                </svg>
              </div>
              <h3>See what your body says</h3>
              <p>
                Connect biosensors (Polar H10) to capture heart rate, HRV, stress markers, and recovery data in real-time. This is what's actually happening inside you - not what you think is happening.
              </p>
            </div>

            <div className="tri-card">
              <div className="tri-icon">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="35" fill="#E8F9F7" stroke="#4ECDC4" strokeWidth="2" />
                  <circle cx="40" cy="40" r="25" fill="none" stroke="#4ECDC4" strokeWidth="2" />
                  <circle cx="40" cy="40" r="15" fill="none" stroke="#4ECDC4" strokeWidth="2" />
                  <circle cx="40" cy="40" r="5" fill="#4ECDC4" />
                </svg>
              </div>
              <h3>Track what matters</h3>
              <p>
                Log scores, results, interactions, and daily performance. This is where psychology and physiology show up in your life - the proof of what's working and what's not.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="features-section">
        <div className="container">
          <h2 className="section-title">From data to clarity</h2>

          <div className="features-list">
            <div className="feature-item">
              <h3>Real-time insights</h3>
              <p>
                Astra doesn't just collect data - it connects the dots. See when mental stress spikes your heart rate before a bad shot. Understand why you perform better on certain days. Know when hidden fatigue is sabotaging results.
              </p>
            </div>

            <div className="feature-item">
              <h3>Personalized guidance</h3>
              <p>
                No generic tips. Astra learns your patterns and gives you specific next steps: breathing exercises when stress peaks, recovery protocols when HRV drops, mental resets when focus breaks.
              </p>
            </div>

            <div className="feature-item">
              <h3>Progress tracking</h3>
              <p>
                Watch your Power Card evolve. See trends over weeks and months. Understand what interventions actually work for you - not theory, but your own data proving what moves the needle.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="trust-section">
        <div className="container">
          <h2 className="section-title">Why athletes, parents, and professionals choose Astra</h2>

          <div className="trust-grid">
            <div className="trust-card">
              <h3>Expert systems, not guesswork</h3>
              <p>
                Our scoring and insights use validated psychology frameworks and proven HRV science - not experimental AI making things up.
              </p>
            </div>

            <div className="trust-card">
              <h3>Your data, your control</h3>
              <p>
                All data stored securely. You own it. Delete anytime. We never sell or share your personal information.
              </p>
            </div>

            <div className="trust-card">
              <h3>Designed for real people</h3>
              <p>
                Child-friendly language for young athletes. Accessible explanations for parents. Professional depth for coaches and clinicians.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="platform-cta">
        <div className="container">
          <h2>Start with Astra Performance</h2>
          <p>
            Our first module focuses on shooting sports - athletes, coaches, and academies use Astra to understand what's blocking peak performance. More modules (relationships, parenting, wellness) coming soon.
          </p>
          <Link to="/signup" className="cta-button">
            Get Early Access
          </Link>
        </div>
      </section>
    </div>
  )
}

export default PlatformPage
