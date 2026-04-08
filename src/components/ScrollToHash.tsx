import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

function ScrollToHash() {
  const location = useLocation()

  useEffect(() => {
    if (!location.hash) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      return
    }

    const id = location.hash.slice(1)

    window.requestAnimationFrame(() => {
      const element = document.getElementById(id)

      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    })
  }, [location.hash, location.pathname])

  return null
}

export default ScrollToHash
