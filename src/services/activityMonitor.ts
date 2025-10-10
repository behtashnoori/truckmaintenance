/**
 * Activity Monitor Service
 * Tracks user activity and manages inactivity timeouts
 */

export interface ActivityMonitorConfig {
  inactivityTimeout: number; // Time in milliseconds before logout
  warningTimeout: number; // Time in milliseconds before showing warning
  checkInterval: number; // How often to check for inactivity (milliseconds)
}

export interface ActivityMonitorCallbacks {
  onInactivity?: () => void;
  onWarning?: () => void;
  onActivity?: () => void;
}

class ActivityMonitor {
  private lastActivityTime: number = Date.now();
  private sessionStartTime: number = Date.now();
  private isMonitoring: boolean = false;
  private intervalId: NodeJS.Timeout | null = null;
  private warningShown: boolean = false;
  
  private config: ActivityMonitorConfig = {
    inactivityTimeout: 30 * 60 * 1000, // 30 minutes
    warningTimeout: 25 * 60 * 1000, // 25 minutes (5 min warning)
    checkInterval: 60 * 1000, // Check every 1 minute
  };
  
  private callbacks: ActivityMonitorCallbacks = {};

  constructor(config?: Partial<ActivityMonitorConfig>) {
    if (config) {
      this.config = { ...this.config, ...config };
    }
    
    // Bind event handlers
    this.handleActivity = this.handleActivity.bind(this);
  }

  /**
   * Start monitoring user activity
   */
  start(callbacks?: ActivityMonitorCallbacks): void {
    if (this.isMonitoring) {
      return;
    }

    if (callbacks) {
      this.callbacks = callbacks;
    }

    this.isMonitoring = true;
    this.lastActivityTime = Date.now();
    this.sessionStartTime = Date.now();
    this.warningShown = false;

    // Add event listeners for user activity
    this.addEventListeners();

    // Start periodic checking
    this.startPeriodicCheck();

    console.log('ActivityMonitor: Started monitoring user activity');
  }

  /**
   * Stop monitoring user activity
   */
  stop(): void {
    if (!this.isMonitoring) {
      return;
    }

    this.isMonitoring = false;
    this.warningShown = false;

    // Remove event listeners
    this.removeEventListeners();

    // Clear interval
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    console.log('ActivityMonitor: Stopped monitoring user activity');
  }

  /**
   * Reset activity timer (call this when user performs an action)
   */
  resetActivity(): void {
    if (!this.isMonitoring) {
      return;
    }

    const wasWarningShown = this.warningShown;
    this.lastActivityTime = Date.now();
    this.warningShown = false;

    // If warning was shown and user is active again, notify
    if (wasWarningShown && this.callbacks.onActivity) {
      this.callbacks.onActivity();
    }

    console.log('ActivityMonitor: Activity reset');
  }

  /**
   * Get time since last activity in milliseconds
   */
  getTimeSinceLastActivity(): number {
    return Date.now() - this.lastActivityTime;
  }

  /**
   * Get time until logout in milliseconds
   */
  getTimeUntilLogout(): number {
    const timeSinceActivity = this.getTimeSinceLastActivity();
    return Math.max(0, this.config.inactivityTimeout - timeSinceActivity);
  }

  /**
   * Get time until warning in milliseconds
   */
  getTimeUntilWarning(): number {
    const timeSinceActivity = this.getTimeSinceLastActivity();
    return Math.max(0, this.config.warningTimeout - timeSinceActivity);
  }

  /**
   * Get session duration in milliseconds
   */
  getSessionDuration(): number {
    return Date.now() - this.sessionStartTime;
  }

  /**
   * Check if warning should be shown
   */
  shouldShowWarning(): boolean {
    return this.getTimeUntilWarning() <= 0 && !this.warningShown;
  }

  /**
   * Check if user should be logged out
   */
  shouldLogout(): boolean {
    return this.getTimeUntilLogout() <= 0;
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<ActivityMonitorConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('ActivityMonitor: Configuration updated', this.config);
  }

  /**
   * Get current configuration
   */
  getConfig(): ActivityMonitorConfig {
    return { ...this.config };
  }

  /**
   * Handle user activity events
   */
  private handleActivity(): void {
    this.resetActivity();
  }

  /**
   * Add event listeners for user activity
   */
  private addEventListeners(): void {
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart',
      'click',
    ];

    events.forEach(event => {
      document.addEventListener(event, this.handleActivity, true);
    });

    // Also listen for visibility change (tab focus/blur)
    document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
  }

  /**
   * Remove event listeners
   */
  private removeEventListeners(): void {
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart',
      'click',
    ];

    events.forEach(event => {
      document.removeEventListener(event, this.handleActivity, true);
    });

    document.removeEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
  }

  /**
   * Handle visibility change (tab focus/blur)
   */
  private handleVisibilityChange(): void {
    if (document.visibilityState === 'visible') {
      // Tab became visible, reset activity
      this.resetActivity();
    }
  }

  /**
   * Start periodic checking for inactivity
   */
  private startPeriodicCheck(): void {
    this.intervalId = setInterval(() => {
      this.checkInactivity();
    }, this.config.checkInterval);
  }

  /**
   * Check for inactivity and trigger appropriate callbacks
   */
  private checkInactivity(): void {
    if (!this.isMonitoring) {
      return;
    }

    // Check if warning should be shown
    if (this.shouldShowWarning()) {
      this.warningShown = true;
      console.log('ActivityMonitor: Showing warning for inactivity');
      if (this.callbacks.onWarning) {
        this.callbacks.onWarning();
      }
    }

    // Check if user should be logged out
    if (this.shouldLogout()) {
      console.log('ActivityMonitor: Logging out due to inactivity');
      if (this.callbacks.onInactivity) {
        this.callbacks.onInactivity();
      }
    }
  }

  /**
   * Get monitoring status
   */
  isActive(): boolean {
    return this.isMonitoring;
  }

  /**
   * Get formatted time until logout
   */
  getFormattedTimeUntilLogout(): string {
    const timeUntilLogout = this.getTimeUntilLogout();
    const minutes = Math.floor(timeUntilLogout / (60 * 1000));
    const seconds = Math.floor((timeUntilLogout % (60 * 1000)) / 1000);
    
    if (minutes > 0) {
      return `${minutes} دقیقه ${seconds} ثانیه`;
    } else {
      return `${seconds} ثانیه`;
    }
  }

  /**
   * Get formatted session duration
   */
  getFormattedSessionDuration(): string {
    const duration = this.getSessionDuration();
    const hours = Math.floor(duration / (60 * 60 * 1000));
    const minutes = Math.floor((duration % (60 * 60 * 1000)) / (60 * 1000));
    
    if (hours > 0) {
      return `${hours} ساعت ${minutes} دقیقه`;
    } else {
      return `${minutes} دقیقه`;
    }
  }
}

// Export singleton instance
export const activityMonitor = new ActivityMonitor();
export default activityMonitor;
