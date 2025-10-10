import { Link } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { Settings, User } from 'lucide-react';

const Index = () => {
  const menuItems = [
    { title: 'خانه', path: '/' },
    { title: 'خدمات', path: '/services' },
    { title: 'درباره', path: '/about' },
    { title: 'تماس با ما', path: '/contact' },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="صفحه اصلی" showBack={false} />
      
      {/* Admin Panel Access - Top Right Corner */}
      <div className="absolute top-20 right-4 z-50 flex gap-2">
        <Button
          asChild
          variant="outline"
          size="sm"
          className="bg-card/80 backdrop-blur-sm border-border/50 hover:bg-accent/50"
        >
          <Link to="/admin/dashboard" className="flex items-center gap-1">
            <Settings className="h-3 w-3" />
            <span className="text-xs">ادمین</span>
          </Link>
        </Button>
        <Button
          asChild
          variant="outline"
          size="sm"
          className="bg-card/80 backdrop-blur-sm border-border/50 hover:bg-accent/50"
        >
          <Link to="/business-expert/dashboard" className="flex items-center gap-1">
            <User className="h-3 w-3" />
            <span className="text-xs">کارشناس</span>
          </Link>
        </Button>
      </div>
      
      <main className="flex-grow flex flex-col items-center justify-center gradient-hero">
        <h1 className="text-3xl md:text-4xl font-bold mb-8 text-center px-4">
          بازارگاه خدمات اضطراری و تعمیرات خودروهای سنگین
        </h1>

        <div className="grid grid-cols-2 gap-4 w-full max-w-md p-4">
          {menuItems.map((item) => (
            <Link
              key={item.title}
              to={item.path}
              className="bg-card rounded-lg shadow-card flex items-center justify-center p-6 text-lg font-medium hover:bg-accent transition-colors"
            >
              {item.title}
            </Link>
          ))}
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Index;
