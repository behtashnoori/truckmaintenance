/**
 * Session Warning Wrapper Component
 * Automatically shows warning modal when session is about to expire
 */

import React, { useEffect, useState } from 'react';
import { useSession } from '@/contexts/SessionContext';
import { authService } from '@/services/auth';
import { SessionWarningModal } from './SessionWarningModal';

export const SessionWarningWrapper: React.FC = () => {
  const { shouldShowWarning, sessionInfo } = useSession();
  const [showModal, setShowModal] = useState(false);

  // Only show warning for authenticated users
  const isAuthenticated = authService.isAuthenticated();

  // Show modal when warning should be displayed
  useEffect(() => {
    if (shouldShowWarning && sessionInfo.isActive && isAuthenticated) {
      setShowModal(true);
    }
  }, [shouldShowWarning, sessionInfo.isActive, isAuthenticated]);

  // Hide modal when session is no longer active
  useEffect(() => {
    if (!sessionInfo.isActive || !isAuthenticated) {
      setShowModal(false);
    }
  }, [sessionInfo.isActive, isAuthenticated]);

  const handleClose = () => {
    setShowModal(false);
  };

  // Don't render anything if user is not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <SessionWarningModal
      isOpen={showModal}
      onClose={handleClose}
    />
  );
};

export default SessionWarningWrapper;
