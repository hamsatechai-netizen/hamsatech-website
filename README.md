# HamsaTech

A React + TypeScript + Vite marketing site for HamsaTech, focused on AI-guided performance, wellness, and personal intelligence.

## Stack

- React 18
- TypeScript
- Vite
- React Router
- Plain CSS

## Routes

- `/` - landing page
- `/home` - main showcase page
- `/platform` - platform details
- `/usecases` - use cases
- `/howitworks` - process overview
- `/about` - about page

## Local Development

```bash
npm install
npm run dev
```

The dev server runs on `http://127.0.0.1:5173` by default.

## Quality Checks

```bash
npm run lint
npm run build
```

## Cloudflare Pages Deployment

This project is ready to deploy as a static site on Cloudflare Pages.

Use these settings:

- Framework preset: `Vite`
- Build command: `npm run build`
- Build output directory: `dist`
- Node version: `18` or newer

Because the app uses client-side routing with `BrowserRouter`, the repo includes a `public/_redirects` file so deep links and refreshes resolve back to `index.html` on Cloudflare Pages.

## Project Structure

```text
src/
  components/
  images/
  styles/
  App.tsx
  main.tsx
```

## Notes

- `dist/` is build output and should not be committed.
- `node_modules/` is ignored.
- Internal navigation is handled with React Router.
