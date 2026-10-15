// Purpose: Render the shared application layout and primary navigation.
import { NavLink } from "react-router-dom";
import { Clock3, Home, Bookmark, Search, Settings, UserRound } from "lucide-react";
import type { ReactNode } from "react";

export function Layout({ children }: { children: ReactNode }) {
  const links = [
    { to: "/", label: "Home", icon: Home },
    { to: "/search", label: "Search", icon: Search },
    { to: "/saved", label: "Saved", icon: Bookmark },
    { to: "/history", label: "History", icon: Clock3 },
    { to: "/settings", label: "Settings", icon: Settings }
  ];

  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="sticky top-0 z-40 border-b border-white/10 bg-zinc-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
          <NavLink to="/" className="text-lg font-black tracking-tight">
            ✦ <span className="gradient-text">CHARLIE MJ INSTA</span>
          </NavLink>
          <nav className="hidden gap-1 md:flex">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-xl px-3 py-2 text-sm transition ${
                    isActive ? "bg-white/10 text-white" : "text-zinc-400 hover:bg-white/5 hover:text-white"
                  }`
                }
              >
                <Icon size={16} /> {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 pb-24">{children}</main>
      <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-white/10 bg-zinc-950/95 p-2 backdrop-blur-xl md:hidden">
        <nav className="flex justify-around">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className="flex flex-col items-center gap-1 px-3 py-1 text-xs text-zinc-400">
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}