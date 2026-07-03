import { useList } from "@refinedev/core";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Circle } from "lucide-react";
import { Link } from "react-router";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { apiFetch } from "@/lib/api";
import type { ChatCompletionStats, ChatRequestLogsList } from "@/types";

const nf = new Intl.NumberFormat();

const num = (value: number | null): string =>
	value == null ? "—" : nf.format(value);
const ms = (value: number | null): string =>
	value == null ? "—" : `${Math.round(value)} ms`;
const pct = (part: number, whole: number): string =>
	whole === 0 ? "—" : `${Math.round((part / whole) * 100)}%`;

function StatCard({
	label,
	value,
	hint,
}: {
	label: string;
	value: string;
	hint?: string;
}) {
	return (
		<Card>
			<CardHeader className="pb-2">
				<CardTitle className="text-sm font-medium text-muted-foreground">
					{label}
				</CardTitle>
			</CardHeader>
			<CardContent>
				<span className="text-2xl font-semibold">{value}</span>
				{hint ? (
					<p className="mt-1 text-xs text-muted-foreground">{hint}</p>
				) : null}
			</CardContent>
		</Card>
	);
}

// The gateway ships with no defaults; an admin must create these resources in order before
// retrieval-augmented chat works. The checklist nudges through that first-run setup.
function SetupChecklist() {
	const providers = useList({
		resource: "providers",
		pagination: { currentPage: 1, pageSize: 1 },
	});
	const embeddingModels = useList({
		resource: "embedding-models",
		pagination: { currentPage: 1, pageSize: 1 },
	});
	const knowledgeBases = useList({
		resource: "knowledge-bases",
		pagination: { currentPage: 1, pageSize: 1 },
	});
	const llmModels = useList({
		resource: "llm-models",
		pagination: { currentPage: 1, pageSize: 1 },
	});

	const steps = [
		{
			label: "Create a provider",
			to: "/providers",
			total: providers.result?.total,
		},
		{
			label: "Add an embedding model",
			to: "/embedding-models",
			total: embeddingModels.result?.total,
		},
		{
			label: "Create a knowledge base",
			to: "/knowledge-bases",
			total: knowledgeBases.result?.total,
		},
		{
			label: "Add an LLM model",
			to: "/llm-models",
			total: llmModels.result?.total,
		},
	];

	const done = steps.filter((step) => (step.total ?? 0) > 0).length;

	// Hide the checklist once everything is in place.
	if (done === steps.length) {
		return null;
	}

	return (
		<Card>
			<CardHeader className="pb-2">
				<CardTitle className="text-sm font-medium">
					Setup{" "}
					<span className="text-muted-foreground">
						({done}/{steps.length})
					</span>
				</CardTitle>
			</CardHeader>
			<CardContent className="flex flex-col gap-1">
				{steps.map((step) => {
					const complete = (step.total ?? 0) > 0;
					return (
						<Link
							key={step.to}
							to={step.to}
							className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-accent"
						>
							{complete ? (
								<CheckCircle2 className="size-4 text-primary" />
							) : (
								<Circle className="size-4 text-muted-foreground" />
							)}
							<span
								className={complete ? "text-muted-foreground line-through" : ""}
							>
								{step.label}
							</span>
						</Link>
					);
				})}
			</CardContent>
		</Card>
	);
}

function RecentFailures() {
	const { data, isLoading } = useQuery({
		queryKey: ["dashboard-recent-failures"],
		queryFn: () =>
			apiFetch<ChatRequestLogsList>(
				"/chat-completion-requests?status=failed&limit=5",
			),
	});

	const failures = data?.requests ?? [];

	return (
		<Card>
			<CardHeader className="pb-2">
				<CardTitle className="text-sm font-medium">Recent failures</CardTitle>
			</CardHeader>
			<CardContent className="flex flex-col gap-2">
				{isLoading ? (
					<Skeleton className="h-16 w-full" />
				) : failures.length === 0 ? (
					<p className="text-sm text-muted-foreground">No recent failures</p>
				) : (
					failures.map((log) => (
						<div
							key={log.id}
							className="flex items-start justify-between gap-3 border-b pb-2 text-sm last:border-0 last:pb-0"
						>
							<div className="min-w-0">
								<span className="font-medium">{log.model_public_id}</span>
								<p className="truncate text-xs text-muted-foreground">
									{log.error_message ?? log.error_code ?? "Unknown error"}
								</p>
							</div>
							<span className="whitespace-nowrap text-xs text-muted-foreground">
								{new Date(log.created_at).toLocaleString()}
							</span>
						</div>
					))
				)}
			</CardContent>
		</Card>
	);
}

export function DashboardPage() {
	const { data, isLoading } = useQuery({
		queryKey: ["dashboard-stats"],
		queryFn: () =>
			apiFetch<ChatCompletionStats>("/chat-completion-requests/stats"),
	});

	return (
		<div className="flex flex-col gap-6">
			<PageHeader title="Dashboard" subtitle="Gateway usage at a glance" />

			{isLoading ? (
				<div className="grid grid-cols-2 gap-4 md:grid-cols-4">
					{Array.from({ length: 4 }).map((_, index) => (
						// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton placeholder
						<Skeleton key={index} className="h-24 w-full" />
					))}
				</div>
			) : data ? (
				<div className="grid grid-cols-2 gap-4 md:grid-cols-4">
					<StatCard label="Total requests" value={num(data.total_requests)} />
					<StatCard
						label="Retrieval requests"
						value={num(data.retrieval_requests)}
						hint={`${pct(data.retrieval_requests, data.total_requests)} of total`}
					/>
					<StatCard label="Total tokens" value={num(data.total_tokens_total)} />
					<StatCard label="Avg latency" value={ms(data.avg_total_ms)} />
				</div>
			) : null}

			<div className="grid gap-4 lg:grid-cols-2">
				<SetupChecklist />
				<RecentFailures />
			</div>

			{data ? (
				<div className="grid gap-6 lg:grid-cols-2">
					<div className="flex flex-col gap-2">
						<h2 className="text-lg font-semibold">Top models</h2>
						<div className="flex flex-col gap-1">
							{data.by_model.length === 0 ? (
								<span className="text-sm text-muted-foreground">No data</span>
							) : (
								data.by_model.slice(0, 5).map((model) => (
									<div
										key={model.model_public_id}
										className="flex items-center justify-between border-b py-1.5 text-sm last:border-0"
									>
										<span className="font-medium">{model.model_public_id}</span>
										<Badge variant="secondary">
											{nf.format(model.requests)} req
										</Badge>
									</div>
								))
							)}
						</div>
					</div>

					<div className="flex flex-col gap-2">
						<h2 className="text-lg font-semibold">Top knowledge bases</h2>
						<div className="flex flex-col gap-1">
							{data.by_knowledge_base.length === 0 ? (
								<span className="text-sm text-muted-foreground">No data</span>
							) : (
								data.by_knowledge_base.slice(0, 5).map((kb) => (
									<div
										key={kb.knowledge_base_id ?? "none"}
										className="flex items-center justify-between border-b py-1.5 text-sm last:border-0"
									>
										<span className="font-medium">
											{kb.knowledge_base_public_id ?? "No retrieval"}
										</span>
										<Badge variant="secondary">
											{nf.format(kb.requests)} req
										</Badge>
									</div>
								))
							)}
						</div>
					</div>
				</div>
			) : null}
		</div>
	);
}
