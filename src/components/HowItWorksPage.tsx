import '../styles/About.css'
import '../styles/FeatureCard.css'

const systemItems = [
  {
    id: 1,
    title: 'Capture',
    description: 'Collect the signals that matter and see them in one place.'
  },
  {
    id: 2,
    title: 'Decode',
    description: 'Turn insight into simple next steps you can execute consistently.'
  },
  {
    id: 3,
    title: 'Guide',
    description: 'Measure progress over time so decisions get clearer and outcomes get better.'
  }
]

function HowItWorksPage() {
  return (
    <section className="about-section">
      <div className="container">
        <h2 className="about-title">How it Works</h2>
        <p className="about-description">
          A simple, repeatable loop that keeps you aligned and compounding improvements over time.
        </p>
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
  )
}

export default HowItWorksPage
