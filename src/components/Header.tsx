import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  title: string;
  showBack?: boolean;
  backTo?: string;
  actions?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  showBack = true,
  backTo = '/',
  actions,
}) => {
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b shadow-card">
      <div className="flex items-center justify-between p-4">
        {showBack ? (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(backTo)}
            className="ml-2"
          >
            <ArrowRight size={20} />
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