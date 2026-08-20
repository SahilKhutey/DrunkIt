import { NavLink, useNavigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Button } from "./ui/Button";

const NAV_ITEMS = [
  { to: "/", label: "Overview", exact: true, adminOnly: false },
  { to: "/retailers", label: "Retailers", exact: false, adminOnly: true },
  { to: "/stores", label: "Stores", exact: false, adminOnly: false },
  { to: "/listings", label: "Listings", exact: false, adminOnly: false },
  { to: "/orders", label: "Orders", exact: false, adminOnly: false },
  { to: "/deliveries", label: "Deliveries", exact: false, adminOnly: true },
];

export function Layout() {
  const { me, isPlatformAdmin, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-56 shrink-0 flex-col border-r border-ink-700 bg-ink-900">
        <div className="border-b border-ink-700 px-5 py-4">
          <span className="font-display text-lg text-parchment">
            Drunk<span className="text-brass-500">It</span>
          </span>
          <p className="label-eyebrow mt-0.5">Staff console</p>
        </div>

        <nav className="flex flex-1 flex-col gap-0.5 p-3">
          {NAV_ITEMS.filter((item) => !item.adminOnly || isPlatformAdmin).map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.exact}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive ? "bg-brass-500/10 text-brass-400" : "text-parchment/60 hover:bg-ink-800 hover:text-parchment"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-ink-700 p-3">
          <p className="truncate text-xs text-parchment/50">{me?.email}</p>
          <p className="label-eyebrow mt-0.5">{me?.role.replace("_", " ")}</p>
          <Button
            variant="ghost"
            size="sm"
            className="mt-2 w-full justify-start px-0"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Log out
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-5xl px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
