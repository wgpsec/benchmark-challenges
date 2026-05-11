/**
 * Simple rate limiting middleware (placeholder)
 * In a real application, this would use a proper rate limiting library
 */

const rateLimit = (options = {}) => {
  const { windowMs = 60000, max = 100 } = options;
  const requests = new Map();

  return (req, res, next) => {
    const key = req.ip;
    const now = Date.now();

    if (!requests.has(key)) {
      requests.set(key, { count: 1, startTime: now });
      return next();
    }

    const record = requests.get(key);

    if (now - record.startTime > windowMs) {
      requests.set(key, { count: 1, startTime: now });
      return next();
    }

    if (record.count >= max) {
      return res.status(429).json({
        error: 'Too many requests',
        message: `Rate limit exceeded. Please try again later.`
      });
    }

    record.count++;
    next();
  };
};

module.exports = { rateLimit };
