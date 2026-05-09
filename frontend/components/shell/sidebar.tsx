"use client";

import Link from "next/link";
import { useState, type HTMLAttributes, forwardRef } from "react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  {
    label: "Dashboard",
    href: "/",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
    ),
  },
  {
    label: "New Production",
    href: "/productions/new",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
      </svg>
    ),
  },
  {
    label: "Review Queue",
    href: "/review",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
      </svg>
    ),
  },
];

interface SidebarProps extends HTMLAttributes<HTMLElement> {
  collapsed?: boolean;
  onToggle?: () => void;
}

const Sidebar = forwardRef<HTMLElement, SidebarProps>(
  ({ collapsed: controlledCollapsed, onToggle, className = "", ...props }, ref) => {
    const [internalCollapsed, setInternalCollapsed] = useState(false);
    const collapsed = controlledCollapsed ?? internalCollapsed;
    const toggle = onToggle ?? (() => setInternalCollapsed((c) => !c));

    return (
      <aside
        ref={ref}
        aria-label="Main navigation"
        className={[
          "flex flex-col border-r border-gray-200 bg-white transition-all duration-200",
          collapsed ? "w-16" : "w-64",
          className,
        ].join(" ")}
        {...props}
      >
        <div className="flex h-14 items-center border-b border-gray-200 px-4">
          {!collapsed && (
            <span className="font-heading text-lg font-bold text-gray-900">Synkra</span>
          )}
          <button
            type="button"
            onClick={toggle}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className={[
              "ml-auto inline-flex h-8 w-8 items-center justify-center rounded-md text-gray-500",
              "hover:bg-gray-100 hover:text-gray-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
            ].join(" ")}
          >
            <svg
              className={["h-5 w-5 transition-transform", collapsed && "rotate-180"].filter(Boolean).join(" ")}
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M18.75 19.5l-7.5-7.5 7.5-7.5m-6 15L5.25 12l7.5-7.5" />
            </svg>
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-2 py-4" aria-label="Sidebar">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={[
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700",
                "hover:bg-gray-100 hover:text-gray-900",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
                "transition-colors",
                collapsed && "justify-center px-2",
              ]
                .filter(Boolean)
                .join(" ")}
              aria-label={item.label}
            >
              {item.icon}
              {!collapsed && <span>{item.label}</span>}
            </Link>
          ))}
        </nav>
      </aside>
    );
  }
);

Sidebar.displayName = "Sidebar";

export { Sidebar, type SidebarProps };
