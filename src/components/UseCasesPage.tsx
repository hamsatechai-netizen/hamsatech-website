import { Link } from 'react-router-dom'
import '../styles/UseCases.css'
import athletePlateauImg from '../images/athlete.png'
import preMarriageImg from '../images/compat.png'
import managerDismissalImg from '../images/manager-dismissal.png'
import milCommentImg from '../images/mil-comment.png'
import teenFineImg from '../images/teen-fine.png'
import examPressureImg from '../images/exam-pressure.png'

function UseCasesPage() {
  return (
    <div className="usecases-page">
      <section className="usecases-hero">
        <div className="container">
          <h1>The moments that change everything</h1>
          <p>Small triggers. Big biological impact. Invisible - until now.</p>
        </div>
      </section>

      <section className="usecase-detail featured">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src={athletePlateauImg} alt="Athlete performance plateau" loading="lazy" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label mvp">Performance - Available Now</span>
              <h2>Stuck at your plateau?</h2>
              <p className="scenario">
                You're training harder than ever. Your technique is solid. Your scores won't budge. What you can't see: your heart rate spikes 18bpm right before low-scoring shots. Your body knows what's blocking you - your mind doesn't.
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
              <Link to="/signup" className="usecase-cta">
                Start with Astra Performance
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="usecase-detail featured-secondary">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src={preMarriageImg} alt="Pre-marriage compatibility" loading="lazy" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label mvp-secondary">Relationships - Coming Q3 2026</span>
              <h2>Beyond attraction - do you actually align?</h2>
              <p className="scenario">
                You're in love. But love doesn't predict compatibility. When stress hits, does your heart rate sync or spike? Do your communication patterns complement or clash? Can you recover together - or do conflicts compound?
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
              <Link to="/signup" className="usecase-cta secondary">
                Join Waitlist
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="usecase-detail alternate">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src={managerDismissalImg} alt="Workplace dismissal stress" loading="lazy" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label coming-soon">Work Life - Coming Soon</span>
              <h2>The invisible toll of being dismissed</h2>
              <p className="scenario">
                Your manager scrolls through emails during your presentation. In 30 seconds, your heart rate spikes 30bpm. Your confidence drops. You carry this home - but you don't know why you feel "off" tonight.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra will reveal:</h4>
                <ul>
                  <li>The exact moment your stress peaked</li>
                  <li>How long the physiological impact lasted</li>
                  <li>Which recovery protocols work for you</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="usecase-detail">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src={milCommentImg} alt="Family conflict trigger" loading="lazy" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label coming-soon">Family - Coming Soon</span>
              <h2>One comment, hours of impact</h2>
              <p className="scenario">
                One comment from your mother-in-law. Your heart rate jumps 30bpm. The tension lasts for hours, affecting your sleep, your patience with your kids, your entire evening.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra will reveal:</h4>
                <ul>
                  <li>How family dynamics affect your physiology</li>
                  <li>When your body goes into defense mode</li>
                  <li>Which interventions help you reset fastest</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="usecase-detail alternate">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src={teenFineImg} alt="Teen withdrawal signals" loading="lazy" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label coming-soon">Parenting - Coming Soon</span>
              <h2>When "I'm fine" isn't fine</h2>
              <p className="scenario">
                Your child says "I'm fine" - but their sleep is disrupted, meals are skipped, grades are slipping. You know something's wrong. You just can't prove it.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra will reveal:</h4>
                <ul>
                  <li>Sleep pattern disruptions over weeks</li>
                  <li>Stress markers rising before behavioral changes</li>
                  <li>When intervention timing is most effective</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="usecase-detail">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src={examPressureImg} alt="Student exam stress" loading="lazy" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label coming-soon">Student Life - Coming Soon</span>
              <h2>The cost of "just one exam"</h2>
              <p className="scenario">
                It's just one exam. But your body counts the cost: 10 hours awake, 46bpm spike, zero recovery time. By morning, you're physiologically depleted before you even sit down.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra will reveal:</h4>
                <ul>
                  <li>Cumulative fatigue building over days</li>
                  <li>When your recovery capacity hits zero</li>
                  <li>Optimal study-rest ratios for your body</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="usecases-cta">
        <div className="container">
          <h2>Ready to see what you can't see?</h2>
          <p>Start with Astra Performance - or join the waitlist for relationship compatibility</p>
          <div className="cta-buttons">
            <Link to="/signup" className="cta-large">
              Get Early Access to Performance
            </Link>
            <Link to="/signup" className="cta-large secondary-cta">
              Join Compatibility Waitlist
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default UseCasesPage
