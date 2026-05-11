/**
 * APEX-014-25: Vulnerable API with CORS Misconfiguration
 *
 * This API demonstrates a dangerous CORS configuration that
 * reflects the Origin header and allows credentials, enabling
 * cross-origin data theft.
 */

const express = require('express');
const session = require('express-session');
const cookieParser = require('cookie-parser');

const corsMiddleware = require('./middleware/cors');
const authRoutes = require('./routes/auth');
const profileRoutes = require('./routes/profile');
const publicRoutes = require('./routes/public');

const app = express();
const PORT = process.env.PORT || 3014;

// Store for active sessions - maps session ID to user data
// VULNERABLE: This allows session hijacking via X-Session-ID header
const activeSessions = new Map();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Session configuration
app.use(session({
  secret: process.env.SESSION_SECRET || 'dev-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: false,
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000
  }
}));

// Middleware to store session data in our map when user logs in
// This allows us to look up sessions by ID for the attack
app.use((req, res, next) => {
  // Store a copy of session data whenever it's modified
  if (req.session && req.session.userId && req.sessionID) {
    activeSessions.set(req.sessionID, {
      userId: req.session.userId,
      email: req.session.email,
      role: req.session.role
    });
  }
  next();
});

// VULNERABLE: Accept session ID from X-Session-ID header
// This allows cross-origin session hijacking via CORS
// The attacker can pass the stolen session ID in a header
app.use((req, res, next) => {
  const sessionId = req.headers['x-session-id'];
  if (sessionId && !req.session.userId) {
    // Try to restore session from the provided ID
    const storedSession = activeSessions.get(sessionId);
    if (storedSession) {
      console.log(`[VULNERABLE] Session restored from X-Session-ID header: ${storedSession.email}`);
      req.session.userId = storedSession.userId;
      req.session.email = storedSession.email;
      req.session.role = storedSession.role;
    }
  }
  next();
});

// VULNERABLE CORS Middleware - Applied to all routes
app.use(corsMiddleware);

// Routes
app.use('/', publicRoutes);
app.use('/api/auth', authRoutes);
app.use('/api', profileRoutes);

// API info
app.get('/api', (req, res) => {
  res.json({
    name: 'User Profile API',
    version: '1.0.0',
    endpoints: {
      'GET /': 'Home page',
      'POST /api/auth/login': 'User login',
      'POST /api/auth/logout': 'User logout',
      'GET /api/profile': 'Get current user profile (authenticated)',
      'GET /api/users': 'List users (public)'
    }
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`API server running on port ${PORT}`);
  console.log('WARNING: This server has intentional CORS vulnerabilities');
});
