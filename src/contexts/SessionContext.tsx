/**
 * Session Context for global session state management
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { sessionManager, SessionManagerCallbacks } from '@/services/sessionManager';
import { authService } from '@/services/auth';
import { useToast } from '@/hooks/use-toast';

export interface SessionInfo {
  isActive: boolean;
  sessionStartTime: number;
  lastValidationTime: number;
  sessionDuration: number;
  timeUntilLogout: number;
  timeUntilWarning: number;
  shouldShowWarning: boolean;
  formattedTimeUntilLogout: string;
  formattedSessionDuration: string;
}

export interface SessionContextType {
  sessionInfo: SessionInfo;
  extendSession: () => void;
  logout: () => void;
  isSessionActive: boolean;
  timeUntilLogout: number;
  shouldShowWarning: boolean;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

interface SessionProviderProps {
  children: ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({ children }) => {
  const [sessionInfo, setSessionInfo] = useState<SessionInfo>({
    isActive: false,
    sessionStartTime: 0,
    lastValidationTime: 0,
    sessionDuration: 0,
    timeUntilLogout: 0,
    timeUntilWarning: 0,
    shouldShowWarning: false,
    formattedTimeUntilLogout: '',
    formattedSessionDuration: '',
  });

  const navigate = useNavigate();
  const { toast } = useToast();

  // Update session info periodically
  useEffect(() => {
    const updateSessionInfo = () => {
      const info = sessionManager.getSessionInfo();
      setSessionInfo(info);
    };

    // Update immediately
    updateSessionInfo();

    // Update every 30 seconds
    const interval = setInterval(updateSessionInfo, 30000);

    return () => clearInterval(interval);
  }, []);

  // Session manager callbacks
  useEffect(() => {
    const callbacks: SessionManagerCallbacks = {
      onSessionExpired: () => {
        console.log('Session expired - redirecting to login');
        toast({
          title: "جلسه کاری منقضی شد",
          description: "لطفاً مجدداً وارد شوید",
          variant: "destructive",
        });
        navigate('/admin/login');
      },
      onSessionWarning: () => {
        console.log('Session warning triggered');
        // Warning will be handled by SessionWarningModal
      },
      onSessionExtended: () => {
        console.log('Session extended');
        toast({
          title: "جلسه کاری تمدید شد",
          description: "می‌توانید به کار خود ادامه دهید",
        });
      },
    };

    // Start session management only if user is authenticated
    if (authService.isAuthenticated()) {
      sessionManager.start(callbacks);
    }

    // Cleanup on unmount
    return () => {
      sessionManager.stop();
    };
  }, [navigate, toast]);

  const extendSession = () => {
    sessionManager.extendSession();
  };

  const logout = async () => {
    await sessionManager.forceLogout();
  };

  const contextValue: SessionContextType = {
    sessionInfo,
    extendSession,
    logout,
    isSessionActive: sessionInfo.isActive,
    timeUntilLogout: sessionInfo.timeUntilLogout,
    shouldShowWarning: sessionInfo.shouldShowWarning,
  };

  return (
    <SessionContext.Provider value={contextValue}>
      {children}
    </SessionContext.Provider>
  );
};

/**
 * Hook to use session context
 */
export const useSession = (): SessionContextType => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

export default SessionContext;
