import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  LayoutDashboard,
  FileText,
  Users,
  Building2,
  BarChart3,
  Settings,
  Home,
  LogOut,
  Tag
} from 'lucide-react'

interface AdminSidebarProps {
  onItemClick?: () => void
}

const AdminSidebar: React.FC<AdminSidebarProps> = ({ onItemClick }) => {
  const location = useLocation()

  // TODO: این مقادیر باید از API دریافت شوند
  const pendingApplications = 12
  const totalUsers = 156

  const menuItems = [
    {
      title: 'داشبورد',
      icon: LayoutDashboard,
      href: '/admin/dashboard',
      badge: null,
      description: 'نمای کلی سیستم'
    },
    {
      title: 'درخواست‌ها',
      icon: FileText,
      href: '/admin/applications',
      badge: pendingApplications,
      description: 'مدیریت درخواست‌های شرکت‌ها'
    },
    {
      title: 'کاربران',
      icon: Users,
      href: '/admin/users',
      badge: null,
      description: 'مدیریت کاربران و کارشناسان'
    },
    {
      title: 'دسته‌بندی‌ها',
      icon: Tag,
      href: '/admin/categories',
      badge: null,
      description: 'مدیریت دسته‌بندی‌های خدمات'
    },
    {
      title: 'شرکت‌ها',
      icon: Building2,
      href: '/admin/companies',
      badge: null,
      description: 'مدیریت شرکت‌های تایید شده'
    },
    {
      title: 'گزارش‌ها',
      icon: BarChart3,
      href: '/admin/reports',
      badge: null,
      description: 'گزارش‌های تحلیلی'
    },
    {
      title: 'تنظیمات',
      icon: Settings,
      href: '/admin/settings',
      badge: null,
      description: 'تنظیمات سیستم'
    }
  ]

  const handleItemClick = () => {
    if (onItemClick) {
      onItemClick()
    }
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800">
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
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'
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
                  variant="secondary" 
                  className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
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
          onClick={() => {
            // TODO: Implement logout logic
            handleItemClick()
          }}
        >
          <LogOut className="mr-2 h-4 w-4" />
          خروج از سیستم
        </Button>
      </div>

      {/* User Info */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
            م
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              مدیر سیستم
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              admin@example.com
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminSidebar

