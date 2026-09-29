/** Layout components */

import { ReactNode } from "react";
import { clsx } from "clsx";
import { Outlet, NavLink, useLocation } from "react-router-dom";
import { PRODUCT_NAME, THEME_COLORS } from "../utils/constants";
import { Badge } from "./Badge";

const navigation = [
  { path: "/", label: "Live", icon: "mic" },
  { path: "/sessions", label: "Sessions", icon: "file-text" },
  { path: "/dashboard", label: "Dashboard", icon: "bar-chart" },
  { path: "/settings", label: "Settings", icon: "settings" },
];

const icons: Record<string, ReactNode> = {
  mic: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h10m-5 0v3" />
    </svg>
  ),
  "file-text": (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  "bar-chart": (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  settings: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
};

export function Sidebar() {
  const location = useLocation();

  return (
    <aside
      className="fixed left-0 top-0 z-40 h-screen w-64 bg-white border-r border-gray-200 flex flex-col"
      aria-label="Main navigation"
    >
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-snapdragon-navy flex items-center gap-2">
          <svg className="w-8 h-8 text-snapdragon-blue" viewBox="0 0 100 100" aria-hidden="true">
            <defs>
              <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor={THEME_COLORS.primary} />
                <stop offset="100%" stopColor={THEME_COLORS.navy} />
              </linearGradient>
            </defs>
            <rect width="100" height="100" rx="20" fill="url(#logoGrad)" />
            <path d="M30 50 L45 65 L70 35" stroke="white" strokeWidth="8" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          {PRODUCT_NAME}
        </h1>
      </div>

      <nav className="flex-1 p-4 space-y-1" role="navigation" aria-label="Pages">
        {navigation.map((item) => {
          const isActive = location.pathname === item.path || (item.path !== "/" && location.pathname.startsWith(item.path));
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-snapdragon-blue-light text-snapdragon-blue"
                    : "text-gray-600 hover:bg-gray-50 hover:text-snapdragon-navy"
                )
              }
              aria-current={isActive ? "page" : undefined}
            >
              {icons[item.icon]}
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-400 text-center">
          Version 0.1.0
        </div>
      </div>
    </aside>
  );
}

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <main className="ml-64 min-h-screen transition-all duration-200" role="main">
        <div className="p-6 md:p-8 lg:p-10">
          <div className="max-w-7xl mx-auto">{children}</div>
        </div>
      </main>
    </div>
  );
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-snapdragon-navy">{title}</h1>
        {subtitle && <p className="text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
}