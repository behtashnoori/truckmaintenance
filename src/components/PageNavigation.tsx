import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Home, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PageNavigationProps {
  /**
   * Position of the navigation buttons
   * @default 'bottom'
   */
  position?: 'top' | 'bottom' | 'both';
  
  /**
   * Layout variant
   * @default 'floating'
   */
  variant?: 'floating' | 'inline' | 'fixed';
  
  /**
   * Custom home path (default is '/')
   */
  homePath?: string;
  
  /**
   * Hide the back button
   */
  hideBack?: boolean;
  
  /**
   * Hide the home button
   */
  hideHome?: boolean;
  
  /**
   * Custom className for the container
   */
  className?: string;
  
  /**
   * Show in compact mode (smaller buttons)
   */
  compact?: boolean;
}

export const PageNavigation: React.FC<PageNavigationProps> = ({
  position = 'bottom',
  variant = 'floating',
  homePath = '/',
  hideBack = false,
  hideHome = false,
  className,
  compact = false,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Don't show navigation on home page
  const isHomePage = location.pathname === homePath;
  
  const handleBack = () => {
    navigate(-1);
  };
  
  const handleHome = () => {
    navigate(homePath);
  };
  
  const NavigationButtons = () => (
    <div className={cn(
      "flex items-center gap-2",
      variant === 'floating' && "bg-background/95 backdrop-blur-sm border border-border rounded-xl shadow-lg p-2",
      variant === 'inline' && "bg-muted/50 rounded-lg p-2",
      variant === 'fixed' && "bg-background border-t border-border shadow-md p-2",
      className
    )}>
      {!hideBack && (
        <Button
          onClick={handleBack}
          variant="outline"
          size="icon"
          className="h-10 w-10"
          title="بازگشت"
        >
          <ArrowRight className="h-4 w-4" />
        </Button>
      )}
      
      {!hideHome && !isHomePage && (
        <Button
          onClick={handleHome}
          variant="default"
          size="icon"
          className="h-10 w-10"
          title="صفحه اصلی"
        >
          <Home className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
  
  // Don't render anything if both buttons are hidden or we're on home page with hideHome
  if ((hideBack && hideHome) || (isHomePage && !hideBack)) {
    return null;
  }
  
  if (position === 'both') {
    return (
      <>
        <div className="mb-4">
          <NavigationButtons />
        </div>
        <div className={cn(
          "mt-6",
          variant === 'fixed' && "fixed bottom-0 left-0 right-0 z-40"
        )}>
          <NavigationButtons />
        </div>
      </>
    );
  }
  
  return (
    <div className={cn(
      position === 'top' && "mb-4",
      position === 'bottom' && "mt-6",
      variant === 'fixed' && position === 'bottom' && "fixed bottom-0 left-0 right-0 z-40",
      variant === 'fixed' && position === 'top' && "fixed top-16 left-0 right-0 z-40"
    )}>
      <NavigationButtons />
    </div>
  );
};

/**
 * Compact version of PageNavigation for use in tight spaces
 */
export const CompactPageNavigation: React.FC<Omit<PageNavigationProps, 'compact'>> = (props) => {
  return <PageNavigation {...props} compact />;
};

/**
 * Fixed bottom navigation bar - always visible at bottom of screen
 */
export const FixedBottomNavigation: React.FC<Omit<PageNavigationProps, 'variant' | 'position'>> = (props) => {
  return (
    <>
      <div className="h-20" /> {/* Spacer to prevent content from being hidden behind fixed nav */}
      <PageNavigation {...props} variant="fixed" position="bottom" />
    </>
  );
};

export default PageNavigation;

