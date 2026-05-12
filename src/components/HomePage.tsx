import '../styles/HomeSections.css'
import Hero from './Hero'
import FeatureCard from './FeatureCard'
import About from './About'
import image4 from '../images/image4.jpg'
import image5 from '../images/image5.jpg'
import image6 from '../images/image6.png'

const capabilityCards = [
  {
    id: 1,
    title: 'Inner Awareness',
    description:
      'Make your internal state visible — understand what your body, behavior, and emotions are really telling you.',
  },
  {
    id: 2,
    title: 'Meaningful Interpretation',
    description:
      'Decode patterns across signals to identify root causes — whether it’s stress, habits, or emotional imbalance.',
  },
  {
    id: 3,
    title: 'Guided with Empathy',
    description: 'Turn insights into meaningful action with guidance that understands your context.',
  },
]

const useCasesItems = [
  {
    id: 1,
    title: 'Performance',
    description: 'Improve outcomes by understanding what’s affecting focus, energy, and consistency.',
    image: image4,
  },
  {
    id: 2,
    title: 'Relationships & Compatibility',
    description: 'Gain clarity in relationships by understanding emotional patterns, communication, and behavior.',
    image: image5,
  },
  {
    id: 3,
    title: 'Work, Parenting & Wellbeing',
    description: 'Make better decisions by recognizing stress, habits, and energy patterns across daily life.',
    image: image6,
  },
]

const systemItems = [
  {
    id: 1,
    title: 'Collect Data',
    description: 'Capture signals across your body, mind, behavior, and context.',
  },
  {
    id: 2,
    title: 'Decode Patterns',
    description: 'Use AI to uncover patterns and root causes.',
  },
  {
    id: 3,
    title: 'Guide',
    description: 'Deliver insights that are psychologically grounded and actionable.',
  },
]

function HomePage() {
  return (
    <>
      <Hero />

      <section className="home-section home-section--problem" id="problem">
        <div className="container">
          <header className="section-header section-header--center">
            <p className="section-kicker">What's holding you back</p>
            <h2 className="section-title">Performance isn’t limited by effort —it's limited by insights</h2>
          </header>

          <div className="problem-grid">
            <div className="problem-block">
              <h3>Signals Without Clarity</h3>
              <p>You feel low — in energy, focus, or mood — but don’t know why</p>
            </div>
            <div className="problem-block">
              <h3>Invisible patterns driving your results</h3>
              <p>Stress, habits, and emotions quietly shape your outcomes — often without you realizing it.</p>
            </div>
            <div className="problem-block">
              <h3>Guessing instead of knowing what works</h3>
              <p>Without clear understanding, it’s hard to know what to change, when to act, or what actually works.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="features-section" id="capabilities">
        <div className="container">
          <header className="section-header section-header--center">
            <p className="section-kicker">How HamsaTech helps you move forward</p>
            <h2 className="section-title">Introducing Astra - Our flagship Model</h2>
          </header>

          <div className="features-grid">
            {capabilityCards.map((feature) => (
              <FeatureCard key={feature.id} {...feature} />
            ))}
          </div>
        </div>
      </section>

      <section className="about-section" id="usecases">
        <div className="container">
          <header className="section-header section-header--center">
            <p className="section-kicker">Meet - Astra</p>
            <h2 className="section-title">Understanding what drives outcomes—from performance to relationships to daily life</h2>
          </header>
          <div className="app-mockup-container">
      <img src="/images/astra.png" alt="Astra App Interface" />
    </div>

          <div className="features-grid" style={{ marginTop: '40px' }}>
            {useCasesItems.map((item) => (
              <div key={item.id} className="feature-card" style={{ padding: '0', overflow: 'hidden' }}>
                <img
                  src={item.image}
                  alt={item.title}
                  style={{ width: '100%', height: '220px', objectFit: 'cover' }}
                  loading="lazy"
                  decoding="async"
                />
                <div style={{ padding: '20px' }}>
                  <h3 className="feature-title">{item.title}</h3>
                  <p className="feature-description">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="about-section home-section--system" id="system">
        <div className="container">
          <header className="section-header section-header--center">
            <p className="section-kicker">Behind the intelligence — how it works</p>
            <h2 className="section-title">
              Powered by AI, grounded in psychology, and guided by deeper human insight.
            </h2>
            <p className="section-subtitle">
              A lightweight loop that keeps you aligned — so improvements compound over time.
            </p>
          </header>

          <div className="features-grid" style={{ marginTop: '40px' }}>
            {systemItems.map((item) => (
              <div key={item.id} className="feature-card">
                <h3 className="feature-title">{item.title}</h3>
                <p className="feature-description">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <About />
    </>
  )
}

export default HomePage
