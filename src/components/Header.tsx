import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  title: string;
  showBack?: boolean;
  backTo?: string | 'previous' | 'services' | 'home';
  backText?: string;
  actions?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  showBack = true,
  backTo = '/',
  backText,
  actions,
}) => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    if (backTo === 'previous') {
      navigate(-1);
    } else if (backTo === 'services') {
      navigate('/services');
    } else if (backTo === 'home') {
      navigate('/');
    } else {
      navigate(backTo);
    }
  };

  const getBackText = () => {
    if (backText) return backText;
    if (backTo === 'services') return 'بازگشت به خدمات';
    if (backTo === 'home') return 'بازگشت به خانه';
    if (backTo === 'previous') return 'بازگشت';
    return 'بازگشت';
  };

  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b shadow-card">
      <div className="flex items-center justify-between p-4">
        {showBack ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleBackClick}
            className="ml-2 flex items-center gap-2"
          >
            <ArrowRight size={16} />
            {getBackText()}
          </Button>
        ) : (
          <div className="w-10" />
        )}
        
        <h1 className="text-lg font-semibold text-center flex-1 truncate">
          {title}
        </h1>
        
        {actions || <div className="w-10" />}
      </div>
    </header>
  );
};