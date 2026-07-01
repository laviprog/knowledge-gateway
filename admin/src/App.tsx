import { Authenticated, Refine } from "@refinedev/core";
import routerProvider, {
	CatchAllNavigate,
	NavigateToResource,
} from "@refinedev/react-router";
import { BrowserRouter, Outlet, Route, Routes } from "react-router";
import { Layout } from "@/components/layout";
import { Toaster } from "@/components/ui/sonner";
import { LoginPage } from "@/pages/login";
import { UsersList } from "@/pages/users";
import { authProvider } from "@/providers/authProvider";
import { dataProvider } from "@/providers/dataProvider";
import { notificationProvider } from "@/providers/notificationProvider";

export function App() {
	return (
		<BrowserRouter>
			<Refine
				dataProvider={dataProvider}
				authProvider={authProvider}
				routerProvider={routerProvider}
				notificationProvider={notificationProvider}
				resources={[
					{ name: "users", list: "/users", meta: { label: "Users" } },
					{
						name: "providers",
						list: "/providers",
						meta: { label: "Providers" },
					},
					{
						name: "knowledge-bases",
						list: "/knowledge-bases",
						meta: { label: "Knowledge bases" },
					},
				]}
				options={{ syncWithLocation: true, disableTelemetry: true }}
			>
				<Routes>
					<Route
						element={
							<Authenticated
								key="authenticated"
								fallback={<CatchAllNavigate to="/login" />}
							>
								<Layout />
							</Authenticated>
						}
					>
						<Route index element={<NavigateToResource resource="users" />} />
						<Route path="/users" element={<UsersList />} />
					</Route>

					<Route
						element={
							<Authenticated key="unauthenticated" fallback={<Outlet />}>
								<NavigateToResource resource="users" />
							</Authenticated>
						}
					>
						<Route path="/login" element={<LoginPage />} />
					</Route>
				</Routes>
			</Refine>
			<Toaster />
		</BrowserRouter>
	);
}
