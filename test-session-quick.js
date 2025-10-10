// Quick test script for session management
// Run this in browser console to test with shorter timeouts

// Set short timeouts for testing (1 minute total, 30 seconds warning)
localStorage.setItem('test_session_timeout', '60000'); // 1 minute
localStorage.setItem('test_warning_timeout', '30000'); // 30 seconds

// Update session manager config
if (window.sessionManager) {
  window.sessionManager.updateConfig({
    sessionTimeoutMinutes: 1, // 1 minute
    warningMinutes: 0.5, // 30 seconds warning
  });
}

console.log('Session timeout set to 1 minute for testing');
console.log('Warning will show after 30 seconds');
console.log('Auto-logout will happen after 1 minute');
