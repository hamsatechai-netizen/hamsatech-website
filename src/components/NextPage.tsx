import { useNavigate } from 'react-router-dom'
import '../styles/Hero.css'
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

      <footer className="footer-section">
        <div className="footer-content">
          <div className="footer-column">
            <h3>HamsaTech</h3>
            <p>Human-centered AI for personal intelligence and measurable growth.</p>
          </div>
          <div className="footer-column">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="/platform">Platform</a></li>
              <li><a href="/usecases">Use Cases</a></li>
              <li><a href="/howitworks">How It Works</a></li>
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
