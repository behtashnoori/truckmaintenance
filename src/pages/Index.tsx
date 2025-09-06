import { Link } from 'react-router-dom';

const Index = () => {
  const menuItems = [
    { title: 'خانه', path: '/' },
    { title: 'خدمات', path: '/services' },
    { title: 'درباره', path: '/about' },
    { title: 'تماس با ما', path: '/contact' },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gradient-hero">
      <h1 className="text-3xl md:text-4xl font-bold mb-8 text-center">
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
    </div>
  );
};

export default Index;
