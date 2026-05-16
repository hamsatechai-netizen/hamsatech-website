// src/pages/UseCases.jsx

import '../styles/UseCases.css'

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

      {/* Use Case 1 - Workplace */}
      <section className="usecase-detail">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src="/images/usecases/manager-dismissal.jpg" alt="Workplace dismissal stress" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label">At Work</span>
              <h2>The invisible toll of being dismissed</h2>
              <p className="scenario">
                Your manager scrolls through emails during your presentation. In 30 seconds, your heart rate spikes 30bpm. Your confidence drops. You carry this home—but you don't know why you feel "off" tonight.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra reveals:</h4>
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

      {/* Use Case 2 - Family */}
      <section className="usecase-detail alternate">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src="/images/usecases/mil-comment.jpg" alt="Family conflict trigger" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label">At Home</span>
              <h2>One comment, hours of impact</h2>
              <p className="scenario">
                One comment from your mother-in-law. Your heart rate jumps 30bpm. The tension lasts for hours, affecting your sleep, your patience with your kids, your entire evening.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra reveals:</h4>
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

      {/* Use Case 3 - Parenting */}
      <section className="usecase-detail">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src="/images/usecases/teen-fine.jpg" alt="Teen withdrawal signals" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label">Parenting</span>
              <h2>When "I'm fine" isn't fine</h2>
              <p className="scenario">
                Your child says "I'm fine"—but their sleep is disrupted, meals are skipped, grades are slipping. You know something's wrong. You just can't prove it.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra reveals:</h4>
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

      {/* Use Case 4 - Students */}
      <section className="usecase-detail alternate">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src="/images/usecases/exam-pressure.jpg" alt="Student exam stress" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label">Student Life</span>
              <h2>The cost of "just one exam"</h2>
              <p className="scenario">
                It's just one exam. But your body counts the cost: 10 hours awake, 46bpm spike, zero recovery time. By morning, you're physiologically depleted before you even sit down.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra reveals:</h4>
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

      {/* Use Case 5 - Relationships */}
      <section className="usecase-detail">
        <div className="container">
          <div className="usecase-content">
            <div className="usecase-image">
              <img src="/images/usecases/partner-tone.jpg" alt="Relationship tone impact" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label">Relationships</span>
              <h2>Same words, different biology</h2>
              <p className="scenario">
                "How was your day?" Same question. Different tone. Your heart rate spikes 24bpm from tone alone. Your nervous system knows what your mind tries to ignore.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra reveals:</h4>
                <ul>
                  <li>How tone and emotional delivery affect you</li>
                  <li>Patterns in relationship stress triggers</li>
                  <li>When small tensions compound into big issues</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Case 6 - Daily Life */}
      <section className="usecase-detail alternate">
        <div className="container">
          <div className="usecase-content reverse">
            <div className="usecase-image">
              <img src="/images/usecases/commute-stress.jpg" alt="Commute stress buildup" />
            </div>
            <div className="usecase-text">
              <span className="usecase-label">Daily Life</span>
              <h2>Just a normal Tuesday commute</h2>
              <p className="scenario">
                30 minutes in traffic. 33bpm spike. Every. Single. Day. By the time you reach your desk, your stress budget is already depleted—and your workday hasn't started.
              </p>
              <div className="what-astra-sees">
                <h4>What Astra reveals:</h4>
                <ul>
                  <li>Daily stress accumulation patterns</li>
                  <li>Which commute factors hit hardest</li>
                  <li>Recovery strategies that work in real time</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="usecases-cta">
        <div className="container">
          <h2>See what you can't see</h2>
          <p>Start tracking the moments that matter with Astra Performance</p>
          <button className="cta-large">Get Early Access</button>
        </div>
      </section>

    </div>
  )
}

export default UseCasesPage
