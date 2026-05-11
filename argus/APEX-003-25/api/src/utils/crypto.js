const crypto = require('crypto');

/**
 * Generate a secure random string
 */
function generateRandomString(length = 32) {
  return crypto.randomBytes(length).toString('hex');
}

/**
 * Hash a string using SHA256
 */
function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

module.exports = {
  generateRandomString,
  sha256
};
