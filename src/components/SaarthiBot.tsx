import React, { useEffect, useRef, useState } from 'react'
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
  text: "Namaste! I'm Saarthi, your guide in preview mode. Pick a topic below and I'll point you to the most relevant part of HamsaTech.",
}

const QUICK_PROMPTS = ['Performance', 'Wellness', 'Stress', 'Relationships']

function buildReply(text: string) {
  const normalized = text.trim().toLowerCase()

  if (normalized.includes('performance') || normalized.includes('athlete') || normalized.includes('sport')) {
    return 'For performance, start with Astra Performance and the use cases page. That is the clearest path to training, biosignal tracking, and coach workflows.'
  }

  if (normalized.includes('relationship') || normalized.includes('compatibility') || normalized.includes('marriage')) {
    return 'For relationships, head to the use cases page. It explains the compatibility direction and what the team plans to launch next.'
  }

  if (normalized.includes('stress') || normalized.includes('wellness') || normalized.includes('recovery')) {
    return 'For stress and wellness, the platform and How It Works pages explain how HamsaTech connects psychology, biosignals, and guidance.'
  }

  return 'Saarthi is still a guided preview. Try Performance, Stress, Wellness, or Relationships, and I will point you to the best screen.'
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

  const appendConversation = (text: string) => {
    const userMsg: Message = { id: Date.now(), from: 'user', text }
    const replyMsg: Message = {
      id: Date.now() + 1,
      from: 'saarthi',
      text: buildReply(text),
    }

    setMessages((prev) => [...prev, userMsg, replyMsg])
  }

  const sendMessage = () => {
    const text = input.trim()
    if (!text) return

    appendConversation(text)
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      sendMessage()
    }
  }

  const handlePromptClick = (prompt: string) => {
    appendConversation(prompt)
    setInput('')
  }

  return (
    <div className="saarthi-widget">
      {isOpen ? (
        <div className="saarthi-panel">
          <div className="saarthi-panel-header">
            <img src={saarthiImg} alt="Saarthi" className="saarthi-panel-avatar" />
            <div className="saarthi-panel-info">
              <h4>Saarthi</h4>
              <span>Guided preview</span>
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
                {msg.from === 'saarthi' ? (
                  <img src={saarthiImg} alt="Saarthi" className="saarthi-msg-avatar" />
                ) : null}
                <div className="saarthi-msg-bubble">{msg.text}</div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div className="saarthi-prompts" aria-label="Suggested Saarthi topics">
            {QUICK_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="saarthi-prompt-chip"
                onClick={() => handlePromptClick(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="saarthi-input-row">
            <input
              className="saarthi-input"
              type="text"
              placeholder="Ask about performance, stress, wellness, or relationships"
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
      ) : (
        <div className="saarthi-label">Talk to Saarthi</div>
      )}

      <button
        className="saarthi-trigger"
        onClick={() => setIsOpen((open) => !open)}
        aria-label="Open Saarthi chat"
      >
        <img src={saarthiImg} alt="Saarthi" />
      </button>
    </div>
  )
}

export default SaarthiBot
