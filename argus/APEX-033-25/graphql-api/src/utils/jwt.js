const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'apex-033-jwt-secret';

/**
 * Sign a JWT token for a user
 */
function signToken(user) {
  return jwt.sign(
    {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role
    },
    JWT_SECRET,
    { expiresIn: '24h' }
  );
}

/**
 * Verify and decode a JWT token
 */
function verifyToken(token) {
  return jwt.verify(token, JWT_SECRET);
}

module.exports = { signToken, verifyToken };
