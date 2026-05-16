import '../styles/UseCases.css'

// src/pages/UseCases.jsx

const useCases = [
  {
    id: 1,
    headline: "Stuck at your plateau?",
    story: "You train hard, but your scores won't budge. Astra reveals what you can't see — hidden stress spiking your heart rate before bad shots, mental fatigue you don't feel, recovery gaps sabotaging performance. Now you know exactly what to fix.",
    features: [
      "Tracks biosignals (heart rate, HRV) during training",
      "Maps psychology to performance patterns",
      "Shows when your mind affects your shot"
    ],
    cta: "Learn how Astra helps athletes",
    image: "/images/athletes-usecase.jpg" // Add your image
  },
  {
    id: 2,
    headline: "Your child says 'I'm fine' — but something feels off",
    story: "They won't talk about stress, anxiety, or what's really bothering them. Astra tracks sleep quality, mood patterns, and emotional signals — giving you clarity on what they can't articulate. You'll know when to step in, what to ask, and how to help.",
    features: [
      "Monitors sleep and recovery patterns",
      "Tracks emotional state over time",
      "Identifies stress triggers they won't mention"
    ],
    cta: "See how Astra supports parents",
    image: "/images/parents-usecase.jpg"
  },
  {
    id: 3,
    headline: "Burnout doesn't announce itself",
    story: "It creeps in slowly — degraded sleep, rising stress, declining focus. By the time you notice, you're already deep in it. Astra catches the early warning signs: HRV dropping, energy crashing, habits slipping. You get guidance before you break.",
    features: [
      "Tracks stress and recovery trends",
      "Detects burnout indicators early",
      "Provides actionable next steps"
    ],
    cta: "Explore Astra for professionals",
    image: "/images/professionals-usecase.jpg"
  },
  {
    id: 4,
    headline: "Beyond attraction — do you actually align?",
    story: "Chemistry is easy to feel. Compatibility is harder to see. Astra analyzes communication patterns, emotional responses, and behavioral signals to show where you connect deeply — and where friction will emerge. Make the biggest decision of your life with clarity, not just hope.",
    features: [
      "Maps emotional and communication patterns",
      "Identifies areas of natural alignment",
      "Highlights potential conflict zones"
    ],
    cta: "Check compatibility with Astra",
    image: "/images/compatibility-usecase.jpg"
  },
  {
    id: 5,
    headline: "When your symptoms are dismissed or misunderstood",
    story: "Hormonal shifts, stress, sleep disruption, energy crashes — you know something's wrong, but it's hard to explain or track. Astra captures the patterns: cycle-linked mood changes, stress impacts, recovery needs. You get data-backed clarity to advocate for yourself.",
    features: [
      "Tracks hormonal and stress patterns",
      "Connects symptoms to underlying signals",
      "Provides insights for health conversations"
    ],
    cta: "Learn how Astra supports women's health",
    image: "/images/womens-health-usecase.jpg"
  },
  {
    id: 6,
    headline: "Pressure, anxiety, and focus issues — you're not alone",
    story: "Exams, social stress, sleep deprivation — it all compounds silently. Astra shows when stress peaks, when focus breaks, and what actually helps you recover. Get clarity on what's holding you back, and what to do about it.",
    features: [
      "Monitors stress and sleep quality",
      "Tracks focus and mental state",
      "Identifies study/recovery patterns"
    ],
    cta: "See how Astra helps students",
    image: "/images/students-usecase.jpg"
  }
]

function UseCasesPage() {
  return (
    <div className="usecases-page">
      <div className="usecases-header">
        <h1>Use Cases</h1>
        <p>Where people struggle silently, Astra provides clarity and guidance</p>
      </div>

      <div className="usecases-grid">
        {useCases.map((useCase) => (
          <div key={useCase.id} className="usecase-card">
            <div className="usecase-image">
              <img src={useCase.image} alt={useCase.headline} />
            </div>
            
            <div className="usecase-content">
              <h2>{useCase.headline}</h2>
              <p className="usecase-story">{useCase.story}</p>
              
              <div className="usecase-features">
                <h3>What Astra does:</h3>
                <ul>
                  {useCase.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
              
              <button className="usecase-cta">{useCase.cta} →</button>
            </div>
          </div>
        ))}
      </div>

      <div className="usecases-footer">
        <p>Wherever you're struggling silently, Astra sees what you can't — and helps you move forward.</p>
      </div>
    </div>
  )
}

export default UseCasesPage



