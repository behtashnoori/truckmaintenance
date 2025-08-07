import React from 'react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-muted border-t p-4 text-center text-sm text-muted-foreground">
      <div className="space-y-2">
        <div className="flex justify-center gap-4">
          <Link to="/about" className="hover:text-foreground transition-smooth">
            درباره ما
          </Link>
          <Link to="/contact" className="hover:text-foreground transition-smooth">
            تماس با ما
          </Link>
          <Link to="/legal/privacy" className="hover:text-foreground transition-smooth">
            حریم خصوصی
          </Link>
          <Link to="/legal/terms" className="hover:text-foreground transition-smooth">
            قوانین
          </Link>
        </div>
        <div className="text-xs">
          © ۱۴۰۳ امداد کامیون. تمامی حقوق محفوظ است.
        </div>
      </div>
    </footer>
  );
};