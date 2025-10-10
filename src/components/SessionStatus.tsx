/**
 * Session Status Indicator Component
 * Shows session status in header/sidebar with time until logout
 */

import React, { useState } from 'react';
import { useSession } from '@/contexts/SessionContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Clock, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';

interface SessionStatusProps {
  variant?: 'badge' | 'button' | 'compact';
  showTime?: boolean;
  showIcon?: boolean;
  className?: string;
}

export const SessionStatus: React.FC<SessionStatusProps> = ({
  variant = 'badge',
  showTime = true,
  showIcon = true,
  className = '',
}) => {
  const { sessionInfo, extendSession } = useSession();
  const [isExtending, setIsExtending] = useState(false);

  const handleExtendSession = async () => {
    setIsExtending(true);
    extendSession();
    setTimeout(() => setIsExtending(false), 1000);
  };

  const getStatusColor = () => {
    const timeUntilLogout = sessionInfo.timeUntilLogout;
    const minutesUntilLogout = timeUntilLogout / (60 * 1000);

    if (minutesUntilLogout <= 5) {
      return 'destructive'; // Red - critical
    } else if (minutesUntilLogout <= 10) {
      return 'secondary'; // Orange - warning
    } else {
      return 'default'; // Green - normal
    }
  };

  const getStatusIcon = () => {
    const timeUntilLogout = sessionInfo.timeUntilLogout;
    const minutesUntilLogout = timeUntilLogout / (60 * 1000);

    if (minutesUntilLogout <= 5) {
      return <AlertTriangle className="w-3 h-3" />;
    } else if (minutesUntilLogout <= 10) {
      return <Clock className="w-3 h-3" />;
    } else {
      return <CheckCircle className="w-3 h-3" />;
    }
  };

  const getStatusText = () => {
    if (!sessionInfo.isActive) {
      return 'غیرفعال';
    }

    const timeUntilLogout = sessionInfo.timeUntilLogout;
    const minutesUntilLogout = timeUntilLogout / (60 * 1000);

    if (minutesUntilLogout <= 1) {
      return 'کمتر از 1 دقیقه';
    } else if (minutesUntilLogout <= 60) {
      return `${Math.floor(minutesUntilLogout)} دقیقه`;
    } else {
      const hours = Math.floor(minutesUntilLogout / 60);
      const minutes = Math.floor(minutesUntilLogout % 60);
      return `${hours}س ${minutes}د`;
    }
  };

  const getTooltipContent = () => {
    if (!sessionInfo.isActive) {
      return 'جلسه کاری غیرفعال است';
    }

    return (
      <div className="text-sm space-y-1">
        <div>مدت جلسه: {sessionInfo.formattedSessionDuration}</div>
        <div>زمان باقی‌مانده: {sessionInfo.formattedTimeUntilLogout}</div>
        <div className="text-xs text-gray-400 mt-2">
          برای تمدید جلسه کلیک کنید
        </div>
      </div>
    );
  };

  if (!sessionInfo.isActive) {
    return null;
  }

  const content = (
    <div className={`flex items-center gap-2 ${className}`}>
      {showIcon && getStatusIcon()}
      {showTime && (
        <span className="text-xs font-medium">
          {getStatusText()}
        </span>
      )}
    </div>
  );

  if (variant === 'button') {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExtendSession}
              disabled={isExtending}
              className={`h-8 ${getStatusColor() === 'destructive' ? 'border-red-200 text-red-600 hover:bg-red-50' : ''}`}
            >
              {isExtending ? (
                <RefreshCw className="w-3 h-3 animate-spin" />
              ) : (
                content
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {getTooltipContent()}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  if (variant === 'compact') {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="cursor-pointer" onClick={handleExtendSession}>
              {showIcon && getStatusIcon()}
            </div>
          </TooltipTrigger>
          <TooltipContent>
            {getTooltipContent()}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  // Default badge variant
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge
            variant={getStatusColor()}
            className={`cursor-pointer hover:opacity-80 transition-opacity ${className}`}
            onClick={handleExtendSession}
          >
            {content}
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          {getTooltipContent()}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default SessionStatus;
