import { Authenticated, Refine } from "@refinedev/core";
import routerProvider, {
	CatchAllNavigate,
	NavigateToResource,
} from "@refinedev/react-router";
import { lazy, Suspense } from "react";
import { BrowserRouter, Outlet, Route, Routes } from "react-router";
import { Layout } from "@/components/layout";
import { PageFallback } from "@/components/page-fallback";
import { Toaster } from "@/components/ui/sonner";
import { authProvider } from "@/providers/authProvider";
import { dataProvider } from "@/providers/dataProvider";
import { notificationProvider } from "@/providers/notificationProvider";

// Pages are code-split: each becomes its own chunk loaded on first navigation.
const LoginPage = lazy(() =>
	import("@/pages/login").then((m) => ({ default: m.LoginPage })),
);
const DashboardPage = lazy(() =>
	import("@/pages/dashboard").then((m) => ({ default: m.DashboardPage })),
);
const UsersList = lazy(() =>
	import("@/pages/users").then((m) => ({ default: m.UsersList })),
);
const ProvidersList = lazy(() =>
	import("@/pages/providers").then((m) => ({ default: m.ProvidersList })),
);
const EmbeddingModelsList = lazy(() =>
	import("@/pages/embedding-models").then((m) => ({
		default: m.EmbeddingModelsList,
	})),
);
const KnowledgeBasesList = lazy(() =>
	import("@/pages/knowledge-bases").then((m) => ({
		default: m.KnowledgeBasesList,
	})),
);
const LlmModelsList = lazy(() =>
	import("@/pages/llm-models").then((m) => ({ default: m.LlmModelsList })),
);
const DocumentsList = lazy(() =>
	import("@/pages/documents").then((m) => ({ default: m.DocumentsList })),
);
const RequestsList = lazy(() =>
	import("@/pages/requests").then((m) => ({ default: m.RequestsList })),
);
const SearchPage = lazy(() =>
	import("@/pages/search").then((m) => ({ default: m.SearchPage })),
);
const AnalyticsPage = lazy(() =>
	import("@/pages/analytics").then((m) => ({ default: m.AnalyticsPage })),
);

export function App() {
	return (
		<BrowserRouter>
			<Refine
				dataProvider={dataProvider}
				authProvider={authProvider}
				routerProvider={routerProvider}
				notificationProvider={notificationProvider}
				resources={[
					{
						name: "dashboard",
						list: "/dashboard",
						meta: { label: "Dashboard" },
					},
					{ name: "users", list: "/users", meta: { label: "Users" } },
					{
						name: "providers",
						list: "/providers",
						meta: { label: "Providers" },
					},
					{
						name: "embedding-models",
						list: "/embedding-models",
						meta: { label: "Embedding models" },
					},
					{
						name: "knowledge-bases",
						list: "/knowledge-bases",
						meta: { label: "Knowledge bases" },
					},
					{
						name: "llm-models",
						list: "/llm-models",
						meta: { label: "LLM models" },
					},
					{
						name: "documents",
						list: "/documents",
						meta: { label: "Documents" },
					},
					{ name: "search", list: "/search", meta: { label: "Search" } },
					{ name: "requests", list: "/requests", meta: { label: "Requests" } },
					{ name: "analytics", list: "/analytics", meta: { label: "Usage" } },
				]}
				options={{ syncWithLocation: true, disableTelemetry: true }}
			>
				<Suspense fallback={<PageFallback />}>
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
							<Route
								index
								element={<NavigateToResource resource="dashboard" />}
							/>
							<Route path="/dashboard" element={<DashboardPage />} />
							<Route path="/users" element={<UsersList />} />
							<Route path="/providers" element={<ProvidersList />} />
							<Route
								path="/embedding-models"
								element={<EmbeddingModelsList />}
							/>
							<Route path="/knowledge-bases" element={<KnowledgeBasesList />} />
							<Route path="/llm-models" element={<LlmModelsList />} />
							<Route path="/documents" element={<DocumentsList />} />
							<Route path="/search" element={<SearchPage />} />
							<Route path="/requests" element={<RequestsList />} />
							<Route path="/analytics" element={<AnalyticsPage />} />
						</Route>

						<Route
							element={
								<Authenticated key="unauthenticated" fallback={<Outlet />}>
									<NavigateToResource resource="dashboard" />
								</Authenticated>
							}
						>
							<Route path="/login" element={<LoginPage />} />
						</Route>
					</Routes>
				</Suspense>
			</Refine>
			<Toaster />
		</BrowserRouter>
	);
}
