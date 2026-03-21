import { useState } from 'react'
import { Link } from 'react-router-dom'
import '../styles/Navigation.css'

function Navigation() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          <span className="logo-icon" aria-hidden="true">
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="32" height="32">
              <circle cx="50" cy="50" r="48" fill="#29a0bc" stroke="#fff" strokeWidth="3" />
              <path d="M28 55 C32 45, 40 35, 50 36 C60 37, 68 47, 72 55 C68 62, 57 72, 50 77 C43 72, 32 62, 28 55 Z" fill="#fff" />
              <path d="M50 28 C46 28, 44 32, 44 36 C44 39, 46 42, 50 42 C54 42, 56 39, 56 36 C56 32, 54 28, 50 28 Z" fill="#ffc107" />
            </svg>
          </span>
          <span className="logo-text">HamsaTech</span>
        </Link>
        
        <button
          className={`menu-toggle ${isOpen ? 'active' : ''}`}
          onClick={() => setIsOpen(!isOpen)}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <ul className={`nav-menu ${isOpen ? 'active' : ''}`}>
          <li><a href="/">Home</a></li>
          <li><a href="/about">About</a></li>
          <li><a href="/home#contact">Contact</a></li>
        </ul>
      </div>
    </nav>
  )
}

export default Navigation
