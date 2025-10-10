import { useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Header } from "@/components/Header";
import { Card, CardContent } from "@/components/ui/card";
import { Home, AlertCircle } from "lucide-react";

const NotFound = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="صفحه یافت نشد" backTo="home" />
      <div className="flex-1 flex items-center justify-center p-6">
      <div className="max-w-md w-full space-y-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center space-y-6">
              <div className="mx-auto w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center">
                <AlertCircle size={32} className="text-destructive" />
              </div>
              
              <div>
                <h1 className="text-4xl font-bold mb-2">۴۰۴</h1>
                <p className="text-xl text-muted-foreground mb-2">صفحه یافت نشد</p>
                <p className="text-sm text-muted-foreground">
                  متأسفانه صفحه‌ای که دنبال آن می‌گردید وجود ندارد
                </p>
              </div>

            </div>
          </CardContent>
        </Card>
        
      </div>
      </div>
    </div>
  );
};

export default NotFound;
