/**
 * Session Manager Service
 * Orchestrates session lifecycle and integrates with AuthService and ActivityMonitor
 */

import { authService } from './auth';
import { activityMonitor, ActivityMonitorCallbacks } from './activityMonitor';

export interface SessionManagerConfig {
  sessionTimeoutMinutes: number;
  warningMinutes: number;
  validationIntervalMinutes: number;
}

export interface SessionManagerCallbacks {
  onSessionExpired?: () => void;
  onSessionWarning?: () => void;
  onSessionExtended?: () => void;
}

class SessionManager {
  private isActive: boolean = false;
  private validationInterval: NodeJS.Timeout | null = null;
  private sessionStartTime: number = 0;
  private lastValidationTime: number = 0;
  
  private config: SessionManagerConfig = {
    sessionTimeoutMinutes: 30,
    warningMinutes: 5,
    validationIntervalMinutes: 5,
  };

  private callbacks: SessionManagerCallbacks = {};

  constructor(config?: Partial<SessionManagerConfig>) {
    if (config) {
      this.config = { ...this.config, ...config };
    }
  }

  /**
   * Start session management
   */
  async start(callbacks?: SessionManagerCallbacks): Promise<void> {
    if (this.isActive) {
      return;
    }

    // Check if user is authenticated
    if (!authService.isAuthenticated()) {
      console.warn('SessionManager: Cannot start - user not authenticated');
      return;
    }

    if (callbacks) {
      this.callbacks = callbacks;
    }

    this.isActive = true;
    this.sessionStartTime = Date.now();
    this.lastValidationTime = Date.now();

    // Configure activity monitor
    const activityConfig = {
      inactivityTimeout: this.config.sessionTimeoutMinutes * 60 * 1000,
      warningTimeout: (this.config.sessionTimeoutMinutes - this.config.warningMinutes) * 60 * 1000,
      checkInterval: 60 * 1000, // Check every minute
    };

    activityMonitor.updateConfig(activityConfig);

    // Start activity monitoring
    const activityCallbacks: ActivityMonitorCallbacks = {
      onInactivity: this.handleInactivity.bind(this),
      onWarning: this.handleWarning.bind(this),
      onActivity: this.handleActivity.bind(this),
    };

    activityMonitor.start(activityCallbacks);

    // Start periodic validation
    this.startPeriodicValidation();

    console.log('SessionManager: Session management started');
  }

  /**
   * Stop session management
   */
  stop(): void {
    if (!this.isActive) {
      return;
    }

    this.isActive = false;

    // Stop activity monitoring
    activityMonitor.stop();

    // Clear validation interval
    if (this.validationInterval) {
      clearInterval(this.validationInterval);
      this.validationInterval = null;
    }

    console.log('SessionManager: Session management stopped');
  }

  /**
   * Extend session (reset activity timer)
   */
  extendSession(): void {
    if (!this.isActive) {
      return;
    }

    activityMonitor.resetActivity();
    
    if (this.callbacks.onSessionExtended) {
      this.callbacks.onSessionExtended();
    }

    console.log('SessionManager: Session extended');
  }

  /**
   * Force logout
   */
  async forceLogout(): Promise<void> {
    console.log('SessionManager: Force logout initiated');
    
    // Stop session management
    this.stop();
    
    // Logout from auth service
    await authService.logout();
    
    // Notify callback
    if (this.callbacks.onSessionExpired) {
      this.callbacks.onSessionExpired();
    }
  }

  /**
   * Validate current session
   */
  async validateSession(): Promise<boolean> {
    if (!this.isActive) {
      return false;
    }

    try {
      // Check if token is still valid
      const isValid = await authService.ensureValidToken();
      
      if (!isValid) {
        console.warn('SessionManager: Session validation failed - token invalid');
        await this.forceLogout();
        return false;
      }

      // Check if token is expired
      if (authService.isTokenExpired()) {
        console.warn('SessionManager: Session validation failed - token expired');
        await this.forceLogout();
        return false;
      }

      this.lastValidationTime = Date.now();
      console.log('SessionManager: Session validation successful');
      return true;

    } catch (error) {
      console.error('SessionManager: Session validation error:', error);
      await this.forceLogout();
      return false;
    }
  }

  /**
   * Get session information
   */
  getSessionInfo() {
    return {
      isActive: this.isActive,
      sessionStartTime: this.sessionStartTime,
      lastValidationTime: this.lastValidationTime,
      sessionDuration: this.isActive ? Date.now() - this.sessionStartTime : 0,
      timeUntilLogout: activityMonitor.getTimeUntilLogout(),
      timeUntilWarning: activityMonitor.getTimeUntilWarning(),
      shouldShowWarning: activityMonitor.shouldShowWarning(),
      formattedTimeUntilLogout: activityMonitor.getFormattedTimeUntilLogout(),
      formattedSessionDuration: activityMonitor.getFormattedSessionDuration(),
    };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<SessionManagerConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // Update activity monitor config if session is active
    if (this.isActive) {
      const activityConfig = {
        inactivityTimeout: this.config.sessionTimeoutMinutes * 60 * 1000,
        warningTimeout: (this.config.sessionTimeoutMinutes - this.config.warningMinutes) * 60 * 1000,
      };
      activityMonitor.updateConfig(activityConfig);
    }

    console.log('SessionManager: Configuration updated', this.config);
  }

  /**
   * Get current configuration
   */
  getConfig(): SessionManagerConfig {
    return { ...this.config };
  }

  /**
   * Handle inactivity timeout
   */
  private async handleInactivity(): Promise<void> {
    console.log('SessionManager: Handling inactivity timeout');
    
    // Toast notification will be handled by SessionContext
    await this.forceLogout();
  }

  /**
   * Handle warning before timeout
   */
  private handleWarning(): void {
    console.log('SessionManager: Handling warning before timeout');
    
    if (this.callbacks.onSessionWarning) {
      this.callbacks.onSessionWarning();
    }
  }

  /**
   * Handle user activity
   */
  private handleActivity(): void {
    console.log('SessionManager: User activity detected');
    // Activity is already handled by activityMonitor.resetActivity()
  }

  /**
   * Start periodic session validation
   */
  private startPeriodicValidation(): void {
    const intervalMs = this.config.validationIntervalMinutes * 60 * 1000;
    
    this.validationInterval = setInterval(async () => {
      await this.validateSession();
    }, intervalMs);

    console.log(`SessionManager: Started periodic validation every ${this.config.validationIntervalMinutes} minutes`);
  }

  /**
   * Check if session management is active
   */
  isSessionActive(): boolean {
    return this.isActive;
  }

  /**
   * Get time until logout in a user-friendly format
   */
  getTimeUntilLogoutFormatted(): string {
    return activityMonitor.getFormattedTimeUntilLogout();
  }

  /**
   * Get session duration in a user-friendly format
   */
  getSessionDurationFormatted(): string {
    return activityMonitor.getFormattedSessionDuration();
  }
}

// Export singleton instance
export const sessionManager = new SessionManager();
export default sessionManager;
