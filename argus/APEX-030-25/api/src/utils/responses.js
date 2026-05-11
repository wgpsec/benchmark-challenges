/**
 * Standard response utilities
 */

const success = (res, data, statusCode = 200) => {
  return res.status(statusCode).json({
    success: true,
    ...data
  });
};

const error = (res, message, statusCode = 400, details = null) => {
  const response = {
    success: false,
    error: message
  };

  if (details) {
    response.details = details;
  }

  return res.status(statusCode).json(response);
};

const notFound = (res, resource = 'Resource') => {
  return error(res, `${resource} not found`, 404);
};

const unauthorized = (res, message = 'Authentication required') => {
  return error(res, message, 401);
};

const forbidden = (res, message = 'Access denied') => {
  return error(res, message, 403);
};

module.exports = {
  success,
  error,
  notFound,
  unauthorized,
  forbidden
};
