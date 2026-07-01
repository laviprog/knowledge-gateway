import { useGetIdentity, useLogout, useMenu } from "@refinedev/core";
import { LogOut } from "lucide-react";
import { Suspense } from "react";
import { NavLink, Outlet } from "react-router";
import { PageFallback } from "@/components/page-fallback";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { SessionUser } from "@/types";

export function Layout() {
	const { data: identity } = useGetIdentity<SessionUser>();
	const { mutate: logout } = useLogout();
	const { menuItems, selectedKey } = useMenu();

	const currentLabel =
		menuItems.find((item) => item.key === selectedKey)?.label ??
		"Knowledge Gateway";

	return (
		<div className="flex min-h-svh bg-muted/40">
			<aside className="flex w-60 flex-col border-r bg-sidebar">
				<div className="flex items-center gap-2 px-4 py-5">
					<div className="flex size-8 items-center justify-center rounded-md bg-primary text-sm font-bold text-primary-foreground">
						KG
					</div>
					<span className="font-semibold">Knowledge Gateway</span>
				</div>
				<nav className="flex flex-1 flex-col gap-0.5 px-3">
					{menuItems.map((item) => (
						<NavLink
							key={item.key}
							to={item.route ?? "/"}
							className={({ isActive }) =>
								cn(
									"rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground",
									isActive && "bg-accent font-medium text-foreground",
								)
							}
						>
							{item.label ?? item.name}
						</NavLink>
					))}
				</nav>
				<div className="border-t p-3">
					<div className="mb-2 flex items-center gap-2 px-2">
						<div className="flex size-7 items-center justify-center rounded-full bg-muted text-xs font-medium uppercase">
							{identity?.name?.slice(0, 2) ?? "?"}
						</div>
						<span className="truncate text-sm text-muted-foreground">
							{identity?.name}
						</span>
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

			<div className="flex flex-1 flex-col">
				<header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b bg-background/80 px-8 backdrop-blur">
					<h1 className="text-sm font-medium">{currentLabel}</h1>
					<ThemeToggle />
				</header>
				<main className="flex-1 p-8">
					<Suspense fallback={<PageFallback />}>
						<Outlet />
					</Suspense>
				</main>
			</div>
		</div>
	);
}
