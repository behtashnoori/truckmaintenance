import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Bell, Menu, Search, User, LogOut, Settings } from 'lucide-react'
import { authService } from '@/services/auth'
import { useToast } from '@/hooks/use-toast'

interface AdminHeaderProps {
  onMenuClick?: () => void
  showMenuButton?: boolean
}

const AdminHeader: React.FC<AdminHeaderProps> = ({ 
  onMenuClick, 
  showMenuButton = false 
}) => {
  const navigate = useNavigate()
  const { toast } = useToast()
  
  // Get current user from auth service
  const currentUser = authService.getCurrentUser()
  
  const user = {
    name: currentUser?.full_name || 'مدیر سیستم',
    email: currentUser?.email || 'admin@example.com',
    avatar: '',
    notifications: 5
  }

  const handleProfile = () => {
    toast({
      title: "پروفایل",
      description: "صفحه پروفایل در حال توسعه است",
    })
  }

  const handleSettings = () => {
    toast({
      title: "تنظیمات",
      description: "صفحه تنظیمات در حال توسعه است",
    })
  }

  const handleLogout = async () => {
    try {
      await authService.logout()
      toast({
        title: "خروج موفق",
        description: "با موفقیت از سیستم خارج شدید",
      })
      navigate('/admin/login')
    } catch (error) {
      console.error('Logout error:', error)
      toast({
        title: "خطا در خروج",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      })
    }
  }

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side - Menu button for mobile */}
          <div className="flex items-center">
            {showMenuButton && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onMenuClick}
                className="lg:hidden mr-2"
              >
                <Menu className="h-5 w-5" />
              </Button>
            )}
            
            {/* Logo/Title */}
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                پنل ادمین
              </h1>
            </div>
          </div>

          {/* Right side - Search, Notifications, Profile */}
          <div className="flex items-center space-x-2 rtl:space-x-reverse">
            {/* Search - Hidden on mobile */}
            <div className="hidden md:block">
              <Button variant="ghost" size="sm" className="relative">
                <Search className="h-4 w-4" />
                <span className="sr-only">جستجو</span>
              </Button>
            </div>

            {/* Notifications */}
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="h-4 w-4" />
              {user.notifications > 0 && (
                <Badge 
                  variant="destructive" 
                  className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
                >
                  {user.notifications}
                </Badge>
              )}
              <span className="sr-only">اعلان‌ها</span>
            </Button>

            {/* Profile Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user.avatar} alt={user.name} />
                    <AvatarFallback className="bg-blue-500 text-white">
                      {user.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user.name}</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="cursor-pointer" onClick={handleProfile}>
                  <User className="mr-2 h-4 w-4" />
                  <span>پروفایل</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer" onClick={handleSettings}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>تنظیمات</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="cursor-pointer text-red-600" onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>خروج</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  )
}

export default AdminHeader

