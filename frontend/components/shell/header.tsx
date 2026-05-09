import { type HTMLAttributes, forwardRef } from "react";

interface HeaderProps extends HTMLAttributes<HTMLElement> {}

const Header = forwardRef<HTMLElement, HeaderProps>(
  ({ className = "", ...props }, ref) => {
    return (
      <header
        ref={ref}
        className={[
          "flex h-14 items-center justify-between border-b border-gray-200 bg-white px-6",
          className,
        ].join(" ")}
        {...props}
      >
        <h1 className="text-lg font-semibold text-gray-900 lg:hidden">
          Synkra
        </h1>

        <div className="ml-auto flex items-center gap-4">
          <div className="relative">
            <button
              type="button"
              aria-label="User menu"
              className={[
                "flex h-8 w-8 items-center justify-center rounded-full bg-gray-200 text-sm font-medium text-gray-600",
                "hover:bg-gray-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
              ].join(" ")}
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
                />
              </svg>
            </button>
          </div>
        </div>
      </header>
    );
  }
);

Header.displayName = "Header";

export { Header, type HeaderProps };
