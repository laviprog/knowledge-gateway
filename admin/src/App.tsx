import { Authenticated, Refine } from "@refinedev/core";
import routerProvider, {
	CatchAllNavigate,
	NavigateToResource,
} from "@refinedev/react-router";
import { BrowserRouter, Outlet, Route, Routes } from "react-router";
import { Layout } from "@/components/layout";
import { Toaster } from "@/components/ui/sonner";
import { AnalyticsPage } from "@/pages/analytics";
import { DocumentsList } from "@/pages/documents";
import { EmbeddingModelsList } from "@/pages/embedding-models";
import { KnowledgeBasesList } from "@/pages/knowledge-bases";
import { LlmModelsList } from "@/pages/llm-models";
import { LoginPage } from "@/pages/login";
import { ProvidersList } from "@/pages/providers";
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
					{
						name: "analytics",
						list: "/analytics",
						meta: { label: "Usage" },
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
						<Route path="/providers" element={<ProvidersList />} />
						<Route path="/embedding-models" element={<EmbeddingModelsList />} />
						<Route path="/knowledge-bases" element={<KnowledgeBasesList />} />
						<Route path="/llm-models" element={<LlmModelsList />} />
						<Route path="/documents" element={<DocumentsList />} />
						<Route path="/analytics" element={<AnalyticsPage />} />
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
