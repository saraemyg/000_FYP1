import { useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'
import {
  Eye,
  Bell,
  BarChart3,
  LogOut,
  Shield,
  User,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

const adminNavItems = [
  { path: '/security', label: 'Live Feed', icon: Eye },
  { path: '/alerts',   label: 'Alert Dashboard', icon: Bell },
  { path: '/performance', label: 'Performance', icon: BarChart3 },
]

const securityNavItems = [
  { path: '/security', label: 'Live Feed', icon: Eye },
  { path: '/alerts',   label: 'Alert Dashboard', icon: Bell },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const navItems = user?.role === 'admin' ? adminNavItems : securityNavItems

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300',
          collapsed ? 'w-16' : 'w-64'
        )}
      >
        {/* Logo */}
        <div className={cn(
          'flex items-center border-b border-gray-200 dark:border-gray-700 h-16 flex-shrink-0',
          collapsed ? 'justify-center px-0' : 'gap-3 px-5'
        )}>
          <Shield className="h-7 w-7 text-blue-600 flex-shrink-0" />
          {!collapsed && (
            <div>
              <p className="text-base font-bold text-gray-900 dark:text-white leading-tight">SecureWatch</p>
              <p className="text-[10px] text-gray-500 dark:text-gray-400">Surveillance System</p>
            </div>
          )}
        </div>

        {/* Nav items */}
        <nav className="flex-1 p-3 space-y-1 overflow-hidden">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                title={collapsed ? item.label : undefined}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  collapsed && 'justify-center',
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                )}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            )
          })}
        </nav>

        {/* User + Logout */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-3 flex-shrink-0">
          {!collapsed && (
            <div className="flex items-center gap-3 mb-3 px-1">
              <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center flex-shrink-0">
                <User className="h-4 w-4 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">{user?.username}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  {user?.role?.replace('_', ' ')}
                </p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            title={collapsed ? 'Sign Out' : undefined}
            className={cn(
              'flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors',
              collapsed && 'justify-center'
            )}
          >
            <LogOut className="h-4 w-4 flex-shrink-0" />
            {!collapsed && 'Sign Out'}
          </button>
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3 top-[72px] w-6 h-6 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex items-center justify-center shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          {collapsed
            ? <ChevronRight className="h-3 w-3 text-gray-500" />
            : <ChevronLeft className="h-3 w-3 text-gray-500" />
          }
        </button>
      </aside>

      {/* Main content */}
      <main className={cn(
        'flex-1 transition-all duration-300 min-h-screen',
        collapsed ? 'pl-16' : 'pl-64'
      )}>
        <Outlet />
      </main>
    </div>
  )
}
