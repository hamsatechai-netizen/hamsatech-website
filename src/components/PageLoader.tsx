import '../styles/PageLoader.css'

function PageLoader() {
  return (
    <div className="page-loader" role="status" aria-live="polite" aria-label="Loading page">
      <div className="page-loader-badge" aria-hidden="true">
        <img
          src="/logo-mark-256.png"
          srcSet="/logo-mark-256.png 1x, /logo-mark-384.png 2x"
          alt=""
          width={56}
          height={56}
          decoding="async"
        />
      </div>
      <div className="page-loader-spinner" aria-hidden="true" />
      <p className="page-loader-text">Loading…</p>
    </div>
  )
}

export default PageLoader

