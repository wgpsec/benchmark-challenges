/**
 * Database configuration
 */

const { Sequelize } = require('sequelize');

const DATABASE_URL = process.env.DATABASE_URL || 'postgres://appuser:apppassword@localhost:5432/appdb';

const sequelize = new Sequelize(DATABASE_URL, {
  dialect: 'postgres',
  logging: false,
  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000
  }
});

module.exports = sequelize;
