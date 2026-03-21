# HamsaTech - AI Sports Performance Platform

A React-based web application showcasing AI-powered sports training and performance optimization solutions.

## Features

- **Interactive Showcase**: Modern, responsive web interface for application demonstration
- **Mock Authentication**: Simple login/logout system with demo users
- **Responsive Design**: Mobile-friendly layout with clean, professional styling
- **Component Architecture**: Well-structured React components with TypeScript

## Demo Authentication

The application includes a mock authentication system for demonstration purposes. You can use these demo accounts:

### Demo Users
- **Email**: `demo@example.com` / **Password**: `demo123`
- **Email**: `user@example.com` / **Password**: `user123`
- **Email**: `admin@example.com` / **Password**: `admin123`

### Features
- Sign up with name, email, and password
- Sign in with existing accounts
- Persistent login state (stored in localStorage)
- User profile display in navigation
- Secure logout functionality

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hamsai
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:5173](http://localhost:5173) in your browser

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/          # React components
│   ├── About.tsx       # About section
│   ├── AuthModal.tsx   # Authentication modal
│   ├── FeatureCard.tsx # Feature showcase cards
│   ├── Hero.tsx        # Hero section
│   ├── Navigation.tsx  # Navigation bar with auth
│   ├── ProjectCard.tsx # Project showcase cards
│   ├── SignIn.tsx      # Sign in form
│   └── SignUp.tsx      # Sign up form
├── context/            # React context providers
│   └── AuthContext.tsx # Authentication context
├── styles/             # CSS stylesheets
└── App.tsx            # Main application component
```

## Authentication System

The mock authentication system provides:
- User registration and login
- Session persistence via localStorage
- User state management with React Context
- Form validation and error handling

## Technologies Used

- **React 18** - UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **CSS3** - Styling with responsive design
- **localStorage** - Client-side data persistence

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Code Quality

The project uses TypeScript for type safety and includes:
- Strict TypeScript configuration
- ESLint for code linting
- Prettier for code formatting

## License

This project is for demonstration purposes.
cd hamsai
```

2. Install dependencies:
```bash
npm install
```

### Firebase Setup

**🚀 Quick Setup (Recommended):**
```bash
npm run setup-firebase
```

**📋 Manual Setup:**

1. **Create Firebase Project**
   - Go to [https://firebase.google.com](https://firebase.google.com)
   - Click "Get Started" or "Create a project"
   - Name your project (e.g., "hamsatech-app")
   - Follow the setup wizard

2. **Enable Email/Password Authentication**
   - In Firebase Console, go to "Authentication" → "Get started"
   - Click "Sign-in method" tab
   - Enable "Email/Password" provider
   - Click "Save"

3. **Get Your Firebase Config**
   - Go to "Project Settings" (gear icon in sidebar)
   - Scroll down to "Your apps" section
   - Click "Add app" → Web app (</>)
   - Register with name "HamsaTech"
   - Copy the config object from the code snippet

4. **Configure Environment Variables**
   - Open `.env` file in your project root
   - Replace the demo values with your Firebase config:
   ```env
   VITE_FIREBASE_API_KEY=AIzaSyC...your_api_key
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
   VITE_FIREBASE_APP_ID=1:123456789:web:abcdef123456
   ```

5. **Restart Development Server**
   ```bash
   npm run dev
   ```

**✅ Test Authentication:**
- Click "Sign In" in the top right
- Try creating an account or signing in
- Authentication should now work with your Firebase project!

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Create production build
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint to check code quality

## Project Structure

```
src/
├── components/          # React components
│   ├── Hero.tsx
│   ├── Navigation.tsx
│   ├── FeatureCard.tsx
│   ├── About.tsx
│   ├── SignIn.tsx      # Sign in form
│   ├── SignUp.tsx      # Sign up form
│   └── AuthModal.tsx   # Auth modal wrapper
├── context/            # React context
│   └── AuthContext.tsx # Authentication context
├── config/             # Configuration files
│   └── firebase.ts     # Firebase setup
├── styles/            # Component styles
├── App.tsx            # Main app component
├── App.css            # App styles
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## Authentication Features

### AuthContext
The `AuthContext` provides authentication state and methods:
- `currentUser` - Currently logged-in user
- `loading` - Loading state during auth checks
- `signup(email, password)` - Create new account
- `login(email, password)` - Sign in with credentials
- `logout()` - Sign out current user

### Components

**SignIn Component** - Email/password sign in form
**SignUp Component** - Account creation form with password validation
**AuthModal** - Modal wrapper for auth forms

## Customization

### Adding to Protected Areas
Wrap components with authentication checks:
```typescript
import { useAuth } from './context/AuthContext'

function ProtectedComponent() {
  const { currentUser } = useAuth()
  
  if (!currentUser) {
    return <div>Please sign in</div>
  }
  
  return <div>Welcome, {currentUser.email}!</div>
}
```

### Styling
Global styles are in `src/index.css`. Auth-related styles are in:
- `src/styles/Auth.css` - Form styling
- `src/styles/AuthModal.css` - Modal styling

## Security Notes

- Environment variables are used for Firebase config (never expose API keys in code)
- Passwords are validated client-side (6+ characters)
- Firebase handles secure password storage
- Session tokens are managed by Firebase

## Building for Production

```bash
npm run build
```

The build output will be generated in the `dist/` directory.

## Troubleshooting

**"Firebase config is missing"**
- Make sure `.env` file exists with all Firebase config values
- Restart the development server after adding `.env`

**"Email/Password authentication is disabled"**
- Go to Firebase Console → Authentication → Sign-in method
- Make sure "Email/Password" provider is enabled

**"Cannot create user" or "User already exists"**
- Check Firebase Console for error details
- Ensure email format is valid
- Check password meets Firebase requirements (6+ characters)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

---

Built with ❤️ using React, Firebase, and Vite

