import '../styles/AppSplash.css'

function AppSplash() {
  return (
    <div className="app-splash" role="status" aria-live="polite" aria-label="Loading application">
      <img
        className="app-splash-logo"
        src="/logo-mark-white-384.png"
        srcSet="/logo-mark-white-256.png 1x, /logo-mark-white-384.png 2x"
        alt="HamsaTech"
        width={140}
        height={140}
        decoding="async"
        fetchPriority="high"
      />
    </div>
  )
}

export default AppSplash
