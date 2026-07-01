import { useGetIdentity, useLogout } from "@refinedev/core";
import { LogOut } from "lucide-react";
import { NavLink, Outlet } from "react-router";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { SessionUser } from "@/types";

const NAV_ITEMS = [
	{ label: "Users", to: "/users" },
	{ label: "Providers", to: "/providers" },
	{ label: "Knowledge bases", to: "/knowledge-bases" },
];

export function Layout() {
	const { data: identity } = useGetIdentity<SessionUser>();
	const { mutate: logout } = useLogout();

	return (
		<div className="flex min-h-svh">
			<aside className="flex w-60 flex-col border-r bg-sidebar p-4">
				<div className="mb-6 px-2 text-lg font-semibold">Knowledge Gateway</div>
				<nav className="flex flex-1 flex-col gap-1">
					{NAV_ITEMS.map((item) => (
						<NavLink
							key={item.to}
							to={item.to}
							className={({ isActive }) =>
								cn(
									"rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent",
									isActive && "bg-accent font-medium",
								)
							}
						>
							{item.label}
						</NavLink>
					))}
				</nav>
				<div className="mt-4 border-t pt-4">
					<div className="mb-2 px-2 text-sm text-muted-foreground">
						{identity?.name}
					</div>
					<Button
						variant="outline"
						size="sm"
						className="w-full"
						onClick={() => logout()}
					>
						<LogOut className="size-4" />
						Sign out
					</Button>
				</div>
			</aside>
			<main className="flex-1 p-8">
				<Outlet />
			</main>
		</div>
	);
}
