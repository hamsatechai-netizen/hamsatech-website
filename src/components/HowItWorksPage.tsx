import { Link } from 'react-router-dom'
import '../styles/HowItWorks.css'

const steps = [
  {
    id: 1,
    number: 'Step 1',
    title: 'Get to Know You',
    headline: 'We start with questions, not sensors',
    description: 'First, you complete a 15-minute psychology assessment. No medical jargon - just questions about how you handle stress, focus, and pressure. This builds your baseline: who you are mentally and emotionally before we measure anything physical.',
    whatYouDo: [
      'Answer psychology questions',
      'Set your goals (performance targets, what you want to improve)',
      'Tell us about your context (training schedule, life factors)',
    ],
    time: '15 minutes',
    visual: 'onboarding',
  },
  {
    id: 2,
    number: 'Step 2',
    title: 'Connect Your Data',
    headline: 'Plug in what your body knows',
    description: 'Connect a Polar H10 heart rate sensor (chest strap, $90). This captures your heart rate and HRV during training, competition, or daily life. No app notifications - Astra runs silently in the background, learning your patterns.',
    whatYouDo: [
      'Pair your Polar H10 sensor (one-time, 2 minutes)',
      'Wear it during sessions (or all day for 24/7 tracking)',
      'Astra captures heart rate, HRV, and stress markers automatically',
    ],
    time: '2 minutes setup, then automatic',
    visual: 'sensor',
  },
  {
    id: 3,
    number: 'Step 3',
    title: 'Track Your Sessions',
    headline: 'Train like you always do - we handle the rest',
    description: "Hit 'Start Session' before training. Astra records your heart rate throughout - during warmup, between shots, in pressure moments. After your session, log your scores. That's it. Astra connects the dots between your mind, body, and performance.",
    whatYouDo: [
      'Start session (1 tap)',
      'Train normally',
      'Log scores after (30 seconds)',
      'Optional: Quick check-in (How do you feel? Energy level?)',
    ],
    time: '30 seconds before/after training',
    visual: 'training',
  },
  {
    id: 4,
    number: 'Step 4',
    title: 'Get Your Insights',
    headline: "See what you couldn't see before",
    description: "After every session, Astra shows you the hidden patterns: when stress spiked, where focus dropped, how your body responded under pressure. You'll see exactly which mental states hurt your performance - and which ones help.",
    examples: [
      'Your heart rate jumps 18bpm right before low-scoring shots',
      'You perform 12% better when pre-session energy is 7+',
      'Hidden fatigue detected: HRV down 22% from baseline',
    ],
    time: 'Instant after session',
    visual: 'insights',
  },
  {
    id: 5,
    number: 'Step 5',
    title: 'Take Action',
    headline: 'Get your next move, not just data',
    description: "Astra doesn't leave you with charts. It tells you what to do: breathing exercises when stress is high, recovery protocols when HRV drops, mental resets when focus breaks. Every recommendation is specific to your patterns - not generic advice.",
    whatYouGet: [
      'Personalized action steps',
      'Breathing and recovery exercises',
      'Training adjustments',
      'Progress tracking over weeks',
    ],
    time: '5-10 minutes of guided action',
    visual: 'action',
  },
  {
    id: 6,
    number: 'Step 6',
    title: 'Watch Yourself Improve',
    headline: 'Your Power Card evolves with you',
    description: "Over weeks and months, watch your Power Card scores improve. Steady Heart gets stronger. Eagle Eye sharpens. You'll see which interventions actually work - not theory, but proof from your own data.",
    whatYouSee: [
      'Power Card trends (week-over-week, month-over-month)',
      'Before and after comparisons',
      'Intervention impact analysis',
      'Coach and parent dashboards (optional)',
    ],
    time: 'Ongoing',
    visual: 'progress',
  },
]

function HowItWorksPage() {
  return (
    <div className="howitworks-page">
      <section className="howitworks-hero">
        <div className="container">
          <h1>Your journey with Astra</h1>
          <p>From setup to insights to real progress - here's what happens when you start</p>
        </div>
      </section>

      <div className="timeline-container">
        <div className="timeline-line"></div>
      </div>

      <section className="steps-section">
        <div className="container">
          {steps.map((step, index) => (
            <div key={step.id} className={`step-card ${index % 2 === 0 ? 'left' : 'right'}`}>
              <div className="step-number-badge">
                <span>{step.number}</span>
              </div>

              <div className="step-content">
                <div className="step-header">
                  <h2>{step.title}</h2>
                  <span className="time-badge">{step.time}</span>
                </div>

                <h3>{step.headline}</h3>
                <p className="step-description">{step.description}</p>

                {step.whatYouDo ? (
                  <div className="step-list">
                    <h4>What you do:</h4>
                    <ul>
                      {step.whatYouDo.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {step.examples ? (
                  <div className="step-examples">
                    <h4>Example insights:</h4>
                    <ul>
                      {step.examples.map((example) => (
                        <li key={example}>{example}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {step.whatYouGet ? (
                  <div className="step-list">
                    <h4>What you get:</h4>
                    <ul>
                      {step.whatYouGet.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {step.whatYouSee ? (
                  <div className="step-list">
                    <h4>What you see:</h4>
                    <ul>
                      {step.whatYouSee.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>

              <div className="step-visual">
                <div className={`visual-placeholder ${step.visual}`}>
                  <span>{step.visual}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="howitworks-cta">
        <div className="container">
          <h2>Ready to see what you can't see?</h2>
          <p>Start with Astra Performance - the first module built for shooting sports athletes</p>
          <div className="cta-buttons">
            <Link to="/signup" className="primary-cta">
              Get Early Access
            </Link>
            <Link to="/usecases" className="secondary-cta">
              Explore Use Cases
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HowItWorksPage
