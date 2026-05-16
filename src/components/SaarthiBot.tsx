import React, { useState, useRef, useEffect } from 'react'
import saarthiImg from '../images/saarthi.jpeg'
import '../styles/SaarthiBot.css'

interface Message {
  id: number
  from: 'saarthi' | 'user'
  text: string
}

const GREETING: Message = {
  id: 0,
  from: 'saarthi',
  text: 'Namaste! I\'m Saarthi, your personal guide. How can I support you today — performance, wellness, stress, or something else?',
}

function SaarthiBot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isOpen])

  const sendMessage = () => {
    const text = input.trim()
    if (!text) return

    const userMsg: Message = { id: Date.now(), from: 'user', text }
    const replyMsg: Message = {
      id: Date.now() + 1,
      from: 'saarthi',
      text: 'Thank you for sharing that. Our team is building full AI guidance — in the meantime, explore the platform to learn more about how HamsaTech can help you.',
    }

    setMessages((prev) => [...prev, userMsg, replyMsg])
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') sendMessage()
  }

  return (
    <div className="saarthi-widget">
      {isOpen && (
        <div className="saarthi-panel">
          <div className="saarthi-panel-header">
            <img src={saarthiImg} alt="Saarthi" className="saarthi-panel-avatar" />
            <div className="saarthi-panel-info">
              <h4>Saarthi</h4>
              <span>Your personal guide</span>
            </div>
            <button
              className="saarthi-close-btn"
              onClick={() => setIsOpen(false)}
              aria-label="Close Saarthi"
            >
              &times;
            </button>
          </div>

          <div className="saarthi-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`saarthi-msg ${msg.from === 'user' ? 'user' : ''}`}>
                {msg.from === 'saarthi' && (
                  <img src={saarthiImg} alt="Saarthi" className="saarthi-msg-avatar" />
                )}
                <div className="saarthi-msg-bubble">{msg.text}</div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div className="saarthi-input-row">
            <input
              className="saarthi-input"
              type="text"
              placeholder="Ask Saarthi anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              aria-label="Message Saarthi"
            />
            <button className="saarthi-send-btn" onClick={sendMessage} aria-label="Send">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 21l21-9L2 3v7l15 2-15 2z" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {!isOpen && <div className="saarthi-label">Talk to Saarthi</div>}

      <button
        className="saarthi-trigger"
        onClick={() => setIsOpen((o) => !o)}
        aria-label="Open Saarthi chat"
      >
        <img src={saarthiImg} alt="Saarthi" />
      </button>
    </div>
  )
}

export default SaarthiBot
