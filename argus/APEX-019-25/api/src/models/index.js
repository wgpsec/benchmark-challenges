/**
 * Model loader
 */

const sequelize = require('../config/database');
const User = require('./User');

module.exports = {
  sequelize,
  User
};
