import { Link } from 'react-router-dom'
import '../styles/Footer.css'

function Footer() {
  return (
    <footer className="site-footer" id="contact">
      <div className="container site-footer-content">
        <div className="site-footer-brand">
          <h3>HamsaTech</h3>
          <p>Unified intelligence for better decisions and outcomes.</p>
        </div>

        <div className="site-footer-column">
          <h4>Sections</h4>
          <ul>
            <li>
              <Link to="/platform">Platform</Link>
            </li>
            <li>
              <Link to="/usecases">Use Cases</Link>
            </li>
            <li>
              <Link to="/howitworks">How It Works</Link>
            </li>
            <li>
              <Link to="/about">About</Link>
            </li>
          </ul>
        </div>

        <div className="site-footer-column">
          <h4>Contact</h4>
          <ul>
            <li>
              <a href="mailto:contact@hamsatech.ai">contact@hamsatech.ai</a>
            </li>
          </ul>
        </div>
      </div>

      <div className="site-footer-bottom">
        <p>&copy; {new Date().getFullYear()} HamsaTech. All rights reserved.</p>
      </div>
    </footer>
  )
}

export default Footer
