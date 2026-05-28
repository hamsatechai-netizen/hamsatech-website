import { useState } from 'react'
import { Link } from 'react-router-dom'
import '../styles/Home.css'
import performanceModule from '../images/performance.jpg'
import relationshipsModule from '../images/relationships.jpg'
import wellbeingModule from '../images/wellbeing.jpg'
import pistolHeroVideo from '../images/Pistol Reel.mp4'
import rifleHeroVideo from '../images/Rifel Lok.mp4'

const heroVideos = [pistolHeroVideo, rifleHeroVideo]

function HomePage() {
  const [heroVideoIndex, setHeroVideoIndex] = useState(0)
  const activeHeroVideo = heroVideos[heroVideoIndex]

  return (
    <div className="home-page">
      <section className="hero-minimal hero-video">
        <video
          key={activeHeroVideo}
          className="hero-video-media"
          autoPlay
          muted
          playsInline
          preload="metadata"
          poster={performanceModule}
          onEnded={() => setHeroVideoIndex((index) => (index + 1) % heroVideos.length)}
        >
          <source src={activeHeroVideo} type="video/mp4" />
        </video>
        <div className="hero-video-shade" aria-hidden="true" />
        <div className="container hero-video-content">
          <p className="hero-eyebrow">Astra Performance</p>
          <h1>HamsaTech</h1>
          <p className="hero-tagline">
            Real-time intelligence for shooting athletes, coaches, and academies.
          </p>
          <div className="hero-cta-buttons">
            <Link to="/coach/login" className="btn-primary-large">
              Open Coach Dashboard
            </Link>
            <Link to="/platform" className="btn-secondary-large">
              Explore Platform
            </Link>
          </div>
        </div>
      </section>

      <section className="problem-section">
        <div className="container">
          <h2 className="section-title">What's holding you back</h2>
          <p className="section-subtitle">Performance isn't limited by effort - it's limited by insights</p>

          <div className="problem-grid">
            <div className="problem-card">
              <h3>You feel off, but don't know why</h3>
              <p>Energy drops. Focus breaks. Mood shifts. You know something's wrong, but can't pinpoint what's causing it.</p>
            </div>

            <div className="problem-card">
              <h3>Invisible patterns driving your results</h3>
              <p>Stress, habits, and emotions quietly shape your outcomes - often without you realizing it.</p>
            </div>

            <div className="problem-card">
              <h3>Guessing instead of knowing what works</h3>
              <p>Without clear understanding, it's hard to know what to change, when to act, or what actually moves the needle.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="astra-intro-section">
        <div className="container">
          <h2 className="section-title">Meet Astra</h2>
          <p className="section-subtitle">
            Understanding what drives outcomes - from performance to relationships to daily life
          </p>

          <div className="modules-grid">
            <div className="module-card">
              <div className="module-image">
                <img src={performanceModule} alt="Performance Module" />
              </div>
              <div className="module-content">
                <div className="module-header">
                  <h3>Performance</h3>
                  <span className="badge available">Available Now</span>
                </div>
                <p>Track biosignals, psychology, and performance. See what's blocking your peak.</p>
              </div>
            </div>

            <div className="module-card">
              <div className="module-image">
                <img src={relationshipsModule} alt="Relationships Module" />
              </div>
              <div className="module-content">
                <div className="module-header">
                  <h3>Relationships &amp; Compatibility</h3>
                  <span className="badge coming-soon">Coming Soon</span>
                </div>
                <p>Understand emotional patterns, communication, and compatibility.</p>
              </div>
            </div>

            <div className="module-card">
              <div className="module-image">
                <img src={wellbeingModule} alt="Life and Wellbeing Module" />
              </div>
              <div className="module-content">
                <div className="module-header">
                  <h3>Life &amp; Wellbeing</h3>
                  <span className="badge coming-soon">Coming Soon</span>
                </div>
                <p>Navigate work, parenting, and wellness with clarity.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="how-we-help-section">
        <div className="container">
          <h2 className="section-title">How HamsaTech helps you move forward</h2>
          <p className="section-subtitle">Understanding you and your body is where we start</p>

          <div className="help-cards-container">
            <div className="help-card-large">
              <h3>See what's really happening inside</h3>
              <p>
                We triangulate psychology, biosignals, and performance - giving you the full picture of what's driving your outcomes.
              </p>
            </div>

            <div className="help-card-large">
              <h3>Understand the patterns</h3>
              <p>
                AI decodes connections between your mental state, body signals, and results - revealing what you couldn't see before.
              </p>
            </div>

            <div className="help-card-large">
              <h3>Get your next move</h3>
              <p>
                Not just data - specific action steps. Breathing exercises when stress peaks. Recovery protocols when HRV drops. Guidance that fits your life.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="astra-performance-section">
        <div className="container">
          <div className="performance-content">
            <div className="performance-header">
              <h2>Start with Astra Performance</h2>
              <p>
                Our first module focuses on shooting sports - athletes, coaches, and academies use Astra to understand what's blocking peak performance. Connect your Polar H10 sensor, complete a psychology assessment, and see what you couldn't see before.
              </p>
            </div>

            <div className="performance-features">
              <div className="feature-row">
                <span className="checkmark" aria-hidden="true">+</span>
                <span>Real-time heart rate and HRV tracking</span>
              </div>
              <div className="feature-row">
                <span className="checkmark" aria-hidden="true">+</span>
                <span>Psychology-to-performance mapping</span>
              </div>
              <div className="feature-row">
                <span className="checkmark" aria-hidden="true">+</span>
                <span>Power Card ability scoring</span>
              </div>
              <div className="feature-row">
                <span className="checkmark" aria-hidden="true">+</span>
                <span>Personalized guidance and insights</span>
              </div>
            </div>

            <Link to="/usecases" className="cta-large">
              Learn More About Performance
            </Link>
          </div>
        </div>
      </section>

      <section className="trust-section-simple">
        <div className="container">
          <h2 className="trust-section-title">Why trust HamsaTech</h2>

          <div className="trust-item-horizontal">
            <div className="trust-icon-circle" aria-hidden="true">+</div>
            <div className="trust-text">
              <h4>Expert systems, not guesswork</h4>
              <p>Validated psychology + proven HRV science</p>
            </div>
          </div>

          <div className="trust-item-horizontal">
            <div className="trust-icon-circle" aria-hidden="true">+</div>
            <div className="trust-text">
              <h4>Your data, your control</h4>
              <p>Secure storage. You own it. Delete anytime.</p>
            </div>
          </div>

          <div className="trust-item-horizontal">
            <div className="trust-icon-circle" aria-hidden="true">+</div>
            <div className="trust-text">
              <h4>Built for real people</h4>
              <p>Child-friendly for athletes. Clear for parents. Deep for professionals.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="final-cta-section">
        <div className="container">
          <h2>Ready to see what you can't see?</h2>
          <Link to="/signup" className="cta-large">
            Get Early Access
          </Link>
        </div>
      </section>
    </div>
  )
}

export default HomePage
