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
    title: "Empathetic AI",
    description:
      "AI that listens to your emotional pulse and responds with wisdom - not just data. We understand context, culture, and the human behind every signal.",
  },
  {
    id: 2,
    title: "Spiritual + Psychological Intelligence",
    description:
      "Inspired by the Bhagavad Gita, yoga, and mindfulness - blended with modern behavioral science to decode stress, identity, and relationships.",
  },
  {
    id: 3,
    title: "Personalized Guidance",
    description:
      "Recommendations that fit your life - your sport, your study pressure, your relationships, your daily wellness - not a generic template.",
  },
]

const useCasesItems = [
  {
    id: 1,
    title: "Athletes & Performers",
    description:
      "Precision mental and physiological coaching for shooters and young athletes pushing for peak performance.",
    image: image4,
  },
  {
    id: 2,
    title: "Students & Families",
    description:
      "Calm academic pressure, build focus, and give families the tools to support their child's emotional growth.",
    image: image5,
  },
  {
    id: 3,
    title: "Professionals & Women",
    description:
      "Address workplace burnout, chronic anxiety, and the unique mental load carried by working women across India.",
    image: image6,
  },
]

const systemItems = [
  {
    id: 1,
    title: "Listen",
    description:
      "Capture emotional, behavioral, and physiological signals through assessments, sensors, and daily check-ins.",
  },
  {
    id: 2,
    title: "Understand",
    description:
      "AI triangulates psychology, bio-data, and performance to reveal root causes - not surface symptoms.",
  },
  {
    id: 3,
    title: "Heal & Grow",
    description:
      "Deliver personalized, culturally-grounded guidance that uplifts, empowers, and compounds over time.",
  },
]

function HomePage() {
  return (
    <>
      <Hero />

      <section className="home-section home-section--problem" id="problem">
        <div className="container">
          <header className="section-header section-header--center">
            <p className="section-kicker">The emotional crisis India can no longer ignore</p>
            <h2 className="section-title">Technology connects us - but rarely understands us</h2>
          </header>

          <div className="problem-grid">
            <div className="problem-block">
              <h3>80% of Indian Youth</h3>
              <p>experience academic stress - with no unified, tech-enabled ecosystem for early detection and emotional guidance.</p>
            </div>
            <div className="problem-block">
              <h3>1 in 7 Indians</h3>
              <p>suffers from mental wellness challenges (NIMHANS 2023). Stigma, lack of access, and digital fatigue block early intervention.</p>
            </div>
            <div className="problem-block">
              <h3>70% of Employees</h3>
              <p>face productivity loss due to mental strain, while 60% of working women report chronic anxiety and fatigue (WHO).</p>
            </div>
          </div>
        </div>
      </section>

      <section className="features-section" id="capabilities">
        <div className="container">
          <header className="section-header section-header--center">
            <p className="section-kicker">How HamsaTech heals, connects, and awakens</p>
            <h2 className="section-title">Understanding you - mind, body, and spirit - is where we start</h2>
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
            <p className="section-kicker">Where HamsaTech creates impact</p>
            <h2 className="section-title">From the shooting range to the classroom to the boardroom - one platform, five transformations.</h2>
          </header>

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
            <p className="section-kicker">Behind the intelligence - how it works</p>
            <h2 className="section-title">
              Powered by AI, grounded in psychology, inspired by Indian wisdom.
            </h2>
            <p className="section-subtitle">
              A continuous loop of listening, understanding, and healing - so growth compounds over time.
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
