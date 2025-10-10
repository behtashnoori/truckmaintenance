import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Settings, User } from 'lucide-react';

export const AdminExpertButtons: React.FC = () => {
  return (
    <div className="fixed top-20 right-4 z-50 flex flex-col gap-2">
      <Link to="/admin/login">
        <Button 
          variant="outline" 
          size="sm" 
          className="text-xs bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent/50"
        >
          <Settings size={14} className="mr-1" />
          پنل ادمین
        </Button>
      </Link>
      <Link to="/business-expert/login">
        <Button 
          variant="outline" 
          size="sm" 
          className="text-xs bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent/50"
        >
          <User size={14} className="mr-1" />
          پنل کارشناس
        </Button>
      </Link>
    </div>
  );
};
