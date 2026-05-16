// src/components/UseCases.tsx (or wherever your file is)

import '../styles/UseCases.css'

// Import all use case images
import athletePlateauImg from '../images/athlete.png'
import preMarriageImg from '../images/compat.png'
import managerDismissalImg from '../images/manager-dismissal.png'
import milCommentImg from '../images/mil-comment.png'
import teenFineImg from '../images/teen-fine.png'
import examPressureImg from '../images/exam-pressure.png'

function UseCasesPage() {
  return (
    <div className="usecases-page">
      
      {/* Hero */}
      <section className="usecases-hero">
        <div className="container">
          <h1>The moments that change everything</h1>
          <p>Small triggers. Big biological impact. Invisible—until now.</p>
        </div>
      </section>

      {/* Use Case 1 - Athletes */}
      <section className="usecase-detail featured">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src={athletePlateauImg} alt="Athlete performance plateau" loading="lazy" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label mvp">Performance • Available Now</span>
              <h2>Stuck at your plateau?</h2>
              <p className="scenario">
                You're training harder than ever. Your technique is solid. Your scores won't budge. What you can't see: your heart rate spikes 18bpm right before low-scoring shots. Your body knows what's blocking you—your mind doesn't.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra reveals:</h4>
                <ul>
                  <li>When your heart rate destabilizes before poor shots</li>
                  <li>How pre-session mental state predicts performance</li>
                  <li>Which breathing patterns keep you in the zone</li>
                  <li>Your unique Power Card: Steady Heart, Eagle Eye, Brain Boss scores</li>
                </ul>
              </div>
              <button className="usecase-cta">Start with Astra Performance →</button>
            </div>
          </div>
        </div>
      </section>

      {/* Use Case 2 - Pre-Marriage */}
      <section className="usecase-detail featured-secondary">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src={preMarriageImg} alt="Pre-marriage compatibility" loading="lazy" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label mvp-secondary">Relationships • Coming Q3 2026</span>
              <h2>Beyond attraction—do you actually align?</h2>
              <p className="scenario">
                You're in love. But love doesn't predict compatibility. When stress hits, does your heart rate sync or spike? Do your communication patterns complement or clash? Can you recover together—or do conflicts compound?
              </p>
              <div className="what-astra-sees">
                <h4>What Astra will reveal:</h4>
                <ul>
                  <li>How your stress responses interact during disagreements</li>
                  <li>Whether your emotional regulation patterns complement each other</li>
                  <li>Which conflict styles lead to resolution vs. escalation</li>
                  <li>Your combined compatibility score across psychology, biology, and behavior</li>
                </ul>
              </div>
              <button className="usecase-cta secondary">Join Waitlist →</button>
            </div>
          </div>
        </div>
      </section>

      {/* Continue with other use cases using imported images... */}
      
      <section className="usecase-detail alternate">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src={managerDismissalImg} alt="Workplace dismissal stress" loading="lazy" />
            </div>
            {/* ... */}
          </div>
        </div>
      </section>

      <section className="usecase-detail">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src={milCommentImg} alt="Family conflict trigger" loading="lazy" />
            </div>
            {/* ... */}
          </div>
        </div>
      </section>

      <section className="usecase-detail alternate">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src={teenFineImg} alt="Teen withdrawal signals" loading="lazy" />
            </div>
            {/* ... */}
          </div>
        </div>
      </section>

      <section className="usecase-detail">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src={examPressureImg} alt="Student exam stress" loading="lazy" />
            </div>
            {/* ... */}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="usecases-cta">
        <div className="container">
          <h2>Ready to see what you can't see?</h2>
          <p>Start with Astra Performance—or join the waitlist for relationship compatibility</p>
          <div className="cta-buttons">
            <button className="cta-large">Get Early Access to Performance</button>
            <button className="cta-large secondary-cta">Join Compatibility Waitlist</button>
          </div>
        </div>
      </section>

    </div>
  )
}

export default UseCasesPage
