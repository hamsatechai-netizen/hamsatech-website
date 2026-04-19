import { useState } from 'react'
import '../styles/ProjectCard.css'

interface ProjectCardProps {
  id: number
  title: string
  description: string
  image: string
  tags: string[]
}

function ProjectCard({ title, description, image, tags }: ProjectCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className={`project-card ${isHovered ? 'hovered' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="card-image-wrapper">
        <div className="card-image">{logo}</div>
      </div>
      
      <div className="card-content">
        <h3 className="card-title">{title}</h3>
        <p className="card-description">{description}</p>
        
        <div className="card-tags">
          {tags.map((tag, index) => (
            <span key={index} className="tag">
              {tag}
            </span>
          ))}
        </div>
        
        <button className="card-button">
          Learn More →
        </button>
      </div>
    </div>
  )
}

export default ProjectCard
