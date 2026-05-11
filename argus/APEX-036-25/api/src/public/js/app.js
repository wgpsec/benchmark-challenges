// APEX-036-25: MFA Bypass - Client-side JavaScript
// This file demonstrates the vulnerable client-side MFA check pattern

/**
 * Authentication state management
 */
const Auth = {
  getToken() {
    return localStorage.getItem('token') || localStorage.getItem('tempToken');
  },

  setToken(token, isTemp = false) {
    if (isTemp) {
      localStorage.setItem('tempToken', token);
    } else {
      localStorage.setItem('token', token);
      localStorage.removeItem('tempToken');
    }
  },

  clearTokens() {
    localStorage.removeItem('token');
    localStorage.removeItem('tempToken');
  },

  isAuthenticated() {
    return !!this.getToken();
  }
};

/**
 * API client
 */
const API = {
  async login(username, password) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return response.json();
  },

  async verifyMfa(code, tempToken) {
    const response = await fetch('/api/auth/verify-mfa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, tempToken })
    });
    return response.json();
  },

  async getProfile() {
    const response = await fetch('/api/profile', {
      headers: { 'Authorization': `Bearer ${Auth.getToken()}` }
    });
    return response.json();
  },

  async getDashboard() {
    const response = await fetch('/api/dashboard', {
      headers: { 'Authorization': `Bearer ${Auth.getToken()}` }
    });
    return response.json();
  }
};

// Export for use in HTML files
window.Auth = Auth;
window.API = API;
