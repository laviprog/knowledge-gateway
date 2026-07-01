import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { apiFetch } from "@/lib/api";
import type { ChatCompletionStats } from "@/types";

const nf = new Intl.NumberFormat();

const num = (value: number | null): string =>
	value == null ? "—" : nf.format(value);
const ms = (value: number | null): string =>
	value == null ? "—" : `${Math.round(value)} ms`;

function StatCard({ label, value }: { label: string; value: string }) {
	return (
		<Card>
			<CardHeader className="pb-2">
				<CardTitle className="text-sm font-medium text-muted-foreground">
					{label}
				</CardTitle>
			</CardHeader>
			<CardContent>
				<span className="text-2xl font-semibold">{value}</span>
			</CardContent>
		</Card>
	);
}

export function AnalyticsPage() {
	const { data, isLoading, isError, error } = useQuery({
		queryKey: ["chat-completion-stats"],
		queryFn: () =>
			apiFetch<ChatCompletionStats>("/chat-completion-requests/stats"),
	});

	return (
		<div className="flex flex-col gap-6">
			<PageHeader title="Usage" subtitle="Chat completion request statistics" />

			{isLoading ? (
				<p className="text-sm text-muted-foreground">Loading…</p>
			) : isError ? (
				<p className="text-sm text-destructive">
					{error instanceof Error ? error.message : "Failed to load statistics"}
				</p>
			) : data ? (
				<Stats data={data} />
			) : null}
		</div>
	);
}

function Stats({ data }: { data: ChatCompletionStats }) {
	return (
		<>
			<div className="grid grid-cols-2 gap-4 md:grid-cols-4">
				<StatCard label="Total requests" value={num(data.total_requests)} />
				<StatCard label="Total tokens" value={num(data.total_tokens_total)} />
				<StatCard label="Prompt tokens" value={num(data.prompt_tokens_total)} />
				<StatCard
					label="Completion tokens"
					value={num(data.completion_tokens_total)}
				/>
				<StatCard label="Avg embedding" value={ms(data.avg_embedding_ms)} />
				<StatCard label="Avg LLM TTFB" value={ms(data.avg_llm_ttfb_ms)} />
				<StatCard
					label="Avg generation"
					value={ms(data.avg_llm_generation_ms)}
				/>
				<StatCard label="Avg total" value={ms(data.avg_total_ms)} />
			</div>

			<div className="flex flex-col gap-2">
				<h2 className="text-lg font-semibold">By status</h2>
				<div className="flex flex-wrap gap-2">
					{data.by_status.length === 0 ? (
						<span className="text-sm text-muted-foreground">No data</span>
					) : (
						data.by_status.map((item) => (
							<Badge key={item.status} variant="secondary" className="text-sm">
								{item.status}: {nf.format(item.count)}
							</Badge>
						))
					)}
				</div>
			</div>

			<div className="flex flex-col gap-2">
				<h2 className="text-lg font-semibold">By model</h2>
				<div className="rounded-md border">
					<Table>
						<TableHeader>
							<TableRow>
								<TableHead>Model</TableHead>
								<TableHead className="text-right">Requests</TableHead>
								<TableHead className="text-right">Total tokens</TableHead>
								<TableHead className="text-right">Avg total</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{data.by_model.length === 0 ? (
								<TableRow>
									<TableCell
										colSpan={4}
										className="text-center text-muted-foreground"
									>
										No data
									</TableCell>
								</TableRow>
							) : (
								data.by_model.map((model) => (
									<TableRow key={model.model_public_id}>
										<TableCell className="font-medium">
											{model.model_public_id}
										</TableCell>
										<TableCell className="text-right">
											{nf.format(model.requests)}
										</TableCell>
										<TableCell className="text-right">
											{num(model.total_tokens)}
										</TableCell>
										<TableCell className="text-right">
											{ms(model.avg_total_ms)}
										</TableCell>
									</TableRow>
								))
							)}
						</TableBody>
					</Table>
				</div>
			</div>
		</>
	);
}
