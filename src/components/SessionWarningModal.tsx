/**
 * Session Warning Modal Component
 * Shows warning before session timeout with countdown and options
 */

import React, { useState, useEffect } from 'react';
import { useSession } from '@/contexts/SessionContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, Clock, LogOut, RefreshCw } from 'lucide-react';

interface SessionWarningModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SessionWarningModal: React.FC<SessionWarningModalProps> = ({
  isOpen,
  onClose,
}) => {
  const { sessionInfo, extendSession, logout } = useSession();
  const [countdown, setCountdown] = useState(0);

  // Update countdown every second
  useEffect(() => {
    if (!isOpen) return;

    const updateCountdown = () => {
      const timeUntilLogout = sessionInfo.timeUntilLogout;
      setCountdown(Math.max(0, Math.floor(timeUntilLogout / 1000)));
    };

    // Update immediately
    updateCountdown();

    // Update every second
    const interval = setInterval(updateCountdown, 1000);

    return () => clearInterval(interval);
  }, [isOpen, sessionInfo.timeUntilLogout]);

  // Auto-close when session is no longer active
  useEffect(() => {
    if (!sessionInfo.isActive) {
      onClose();
    }
  }, [sessionInfo.isActive, onClose]);

  const handleExtendSession = () => {
    extendSession();
    onClose();
  };

  const handleLogout = async () => {
    await logout();
    onClose();
  };

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    } else {
      return `${remainingSeconds} ثانیه`;
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <Card className="w-full max-w-md mx-4 shadow-2xl border-2 border-orange-200">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
            <AlertTriangle className="w-8 h-8 text-orange-600" />
          </div>
          <CardTitle className="text-xl font-bold text-orange-800">
            هشدار انقضای جلسه
          </CardTitle>
          <CardDescription className="text-gray-600">
            جلسه کاری شما به زودی منقضی خواهد شد
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Countdown Timer */}
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-orange-600" />
              <span className="text-sm text-gray-600">زمان باقی‌مانده:</span>
            </div>
            <div className="text-3xl font-bold text-orange-600 font-mono">
              {formatTime(countdown)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              در صورت عدم فعالیت، به طور خودکار خارج خواهید شد
            </p>
          </div>

          {/* Session Info */}
          <div className="bg-gray-50 rounded-lg p-3 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">مدت جلسه:</span>
              <span className="font-medium">{sessionInfo.formattedSessionDuration}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <Button
              onClick={handleExtendSession}
              className="w-full bg-green-600 hover:bg-green-700 text-white"
              size="lg"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              ادامه کار
            </Button>
            
            <Button
              onClick={handleLogout}
              variant="outline"
              className="w-full border-red-200 text-red-600 hover:bg-red-50"
              size="lg"
            >
              <LogOut className="w-4 h-4 mr-2" />
              خروج از سیستم
            </Button>
          </div>

          {/* Info Text */}
          <div className="text-center">
            <p className="text-xs text-gray-500">
              با کلیک روی "ادامه کار" جلسه شما تمدید خواهد شد
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SessionWarningModal;
