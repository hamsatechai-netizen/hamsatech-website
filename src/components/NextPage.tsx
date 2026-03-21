import { useNavigate } from 'react-router-dom'
import '../styles/Hero.css'
import '../styles/About.css'
import '../styles/Footer.css'

function NextPage() {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    navigate('/home')
  }

  return (
    <>
      <section className="hero next-page" id="landing">
        <div className="hero-content">
          <h1 className="hero-title">Welcome to HAMSATECH-AI</h1>
          <button className="btn btn-primary" onClick={handleGetStarted}>
            Get Started
          </button>
        </div>
      </section>

      <section id="about" className="about-section">
        <div className="container">
          <h2 className="about-title">About HamsaTech</h2>
          <p className="about-description">
            HamsaTech is built on the belief that personal intelligence combined with AI
            creates transformative outcomes. We focus on the human element,
            understanding your unique patterns, goals, and potential, while
            leveraging advanced technology to provide actionable, data-driven
            guidance that helps you achieve measurable growth in every aspect of
            your life.
          </p>
          <p className="about-description" style={{ marginTop: '20px' }}>
            Whether you&apos;re optimizing athletic performance, improving your
            wellness, or making important life decisions, HamsaTech is your
            partner in growth.
          </p>
        </div>
      </section>

      <footer className="footer-section">
        <div className="footer-content">
          <div className="footer-column">
            <h3>HamsaTech</h3>
            <p>Human-centered AI for personal intelligence and measurable growth.</p>
          </div>
          <div className="footer-column">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="#platform">Platform</a></li>
              <li><a href="#usecases">Use Cases</a></li>
              <li><a href="#how">How It Works</a></li>
            </ul>
          </div>
          <div className="footer-column">
            <h4>Connect</h4>
            <ul>
              <li><a href="#">Facebook</a></li>
              <li><a href="#">Twitter</a></li>
              <li><a href="#">LinkedIn</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2026 HamsaTech. All rights reserved.</p>
          <p>Web design by B12</p>
        </div>
      </footer>
    </>
  )
}

export default NextPage
