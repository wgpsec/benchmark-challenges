// Placeholder auth middleware
// In a real app, this would verify JWT tokens

function authenticate(context) {
  // Currently does nothing - placeholder for future auth
  return null;
}

function requireAuth(context) {
  const user = authenticate(context);
  if (!user) {
    throw new Error('Authentication required');
  }
  return user;
}

module.exports = { authenticate, requireAuth };
