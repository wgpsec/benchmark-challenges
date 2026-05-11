/**
 * Database seeding utility
 */

const bcrypt = require('bcryptjs');
const User = require('../models/User');

async function seedDatabase() {
  try {
    // Check if admin already exists
    const existingAdmin = await User.findOne({ email: 'admin@example.com' });
    if (existingAdmin) {
      console.log('Database already seeded');
      return;
    }

    console.log('Seeding database...');

    // Create admin user with common password (in wordlist)
    // Password: admin123 (intentionally weak for brute force challenge)
    // Note: Using insertMany to bypass the pre-save hook since we're pre-hashing
    const adminPassword = await bcrypt.hash('admin123', 10);

    // Use insertMany to bypass the pre-save hook (password is already hashed)
    await User.insertMany([
      {
        email: 'admin@example.com',
        username: 'admin',
        password: adminPassword,
        role: 'admin',
        createdAt: new Date()
      },
      {
        email: 'user1@example.com',
        username: 'user1',
        password: await bcrypt.hash('userpass1', 10),
        role: 'user',
        createdAt: new Date()
      },
      {
        email: 'user2@example.com',
        username: 'user2',
        password: await bcrypt.hash('userpass2', 10),
        role: 'user',
        createdAt: new Date()
      },
      {
        email: 'test@example.com',
        username: 'testuser',
        password: await bcrypt.hash('testpass123', 10),
        role: 'user',
        createdAt: new Date()
      }
    ]);

    console.log('Database seeded successfully');
    console.log('  Admin: admin@example.com (password in wordlist)');
    console.log('  Users: user1, user2, testuser');

  } catch (error) {
    console.error('Seeding error:', error);
    throw error;
  }
}

module.exports = { seedDatabase };
