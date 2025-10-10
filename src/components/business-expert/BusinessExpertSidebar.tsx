import React, { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { apiFetch } from '@/utils/api'
import { authService } from '@/services/auth'
import { SessionStatus } from '@/components/SessionStatus'
import {
  LayoutDashboard,
  Search,
  CheckCircle,
  DollarSign,
  MessageCircle,
  Home,
  LogOut,
  FileCheck,
  TrendingUp,
  Building,
  Users,
  Upload
} from 'lucide-react'

interface BusinessExpertSidebarProps {
  onItemClick?: () => void
}

const BusinessExpertSidebar: React.FC<BusinessExpertSidebarProps> = ({ onItemClick }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const [pendingReviews, setPendingReviews] = useState<number>(0)
  const [approvedToday, setApprovedToday] = useState<number>(0)
  const [monthlyRevenue, setMonthlyRevenue] = useState<string>('0')
  const currentUser = authService.getCurrentUser()

  // Load sidebar data from API
  useEffect(() => {
    const loadSidebarData = async () => {
      try {
        // Get pending applications count
        const pendingResponse = await apiFetch('/api/business-expert/applications?status=pending&per_page=1');
        setPendingReviews(pendingResponse.total || 0);

        // Get today's approved count (you might need to implement this endpoint)
        // For now, we'll set it to 0
        setApprovedToday(0);

        // Get monthly revenue (you might need to implement this endpoint)
        // For now, we'll set it to 0
        setMonthlyRevenue('0');
      } catch (error) {
        console.error('Error loading sidebar data:', error);
        // Keep default values on error
      }
    };

    loadSidebarData();
  }, []);

  const menuItems = [
    {
      title: 'داشبورد',
      icon: LayoutDashboard,
      href: '/business-expert/dashboard',
      badge: null,
      description: 'نمای کلی کارشناسی'
    },
    {
      title: 'بررسی درخواست‌ها',
      icon: Search,
      href: '/business-expert/applications',
      badge: pendingReviews,
      description: 'بررسی و تایید درخواست‌ها'
    },
    {
      title: 'مدیریت ارائه‌دهندگان',
      icon: Building,
      href: '/business-expert/providers',
      badge: null,
      description: 'مدیریت ارائه‌دهندگان خدمات'
    },
    {
      title: 'اضافه کردن ارائه‌دهنده',
      icon: Upload,
      href: '/business-expert/providers/add',
      badge: null,
      description: 'اضافه کردن ارائه‌دهنده جدید'
    },
    {
      title: 'آپلود انبوه',
      icon: Upload,
      href: '/business-expert/providers/bulk-upload',
      badge: null,
      description: 'آپلود انبوه ارائه‌دهندگان'
    }
  ]

  const handleItemClick = () => {
    if (onItemClick) {
      onItemClick()
    }
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800">
      {/* Quick Stats */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
            <div className="flex items-center space-x-2 rtl:space-x-reverse">
              <FileCheck className="h-4 w-4 text-blue-600" />
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">در انتظار بررسی</p>
                <p className="text-lg font-semibold text-blue-600">{pendingReviews}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
            <div className="flex items-center space-x-2 rtl:space-x-reverse">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">تایید امروز</p>
                <p className="text-lg font-semibold text-green-600">{approvedToday}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-4 py-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              to={item.href}
              onClick={handleItemClick}
              className={cn(
                'flex items-center justify-between px-3 py-3 rounded-lg text-sm font-medium transition-colors',
                'hover:bg-gray-100 dark:hover:bg-gray-700',
                isActive
                  ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300'
                  : 'text-gray-700 dark:text-gray-300'
              )}
            >
              <div className="flex items-center space-x-3 rtl:space-x-reverse">
                <Icon className="h-5 w-5 flex-shrink-0" />
                <div className="flex flex-col">
                  <span className="font-medium">{item.title}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {item.description}
                  </span>
                </div>
              </div>
              
              {item.badge && (
                <Badge 
                  variant={typeof item.badge === 'string' ? "default" : "secondary"}
                  className={
                    typeof item.badge === 'string' 
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      : "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                  }
                >
                  {item.badge}
                </Badge>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
        {/* Back to Main Site */}
        <Link to="/" onClick={handleItemClick}>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-gray-600 dark:text-gray-400"
          >
            <Home className="mr-2 h-4 w-4" />
            بازگشت به سایت اصلی
          </Button>
        </Link>

        {/* Logout */}
        <Button 
          variant="ghost" 
          className="w-full justify-start text-red-600 dark:text-red-400"
          onClick={async () => {
            try {
              await authService.logout()
              handleItemClick()
              navigate('/admin/login')
            } catch (error) {
              console.error('Logout error:', error)
              navigate('/admin/login')
            }
          }}
        >
          <LogOut className="mr-2 h-4 w-4" />
          خروج از سیستم
        </Button>
      </div>

      {/* User Info */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
            {currentUser?.full_name?.charAt(0) || 'ک'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {currentUser?.full_name || 'کارشناس بازرگانی'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {currentUser?.email || 'expert@example.com'}
            </p>
          </div>
        </div>
        
        {/* Session Status */}
        <div className="mt-3">
          <SessionStatus variant="badge" showTime={true} showIcon={true} />
        </div>
      </div>
    </div>
  )
}

export default BusinessExpertSidebar

