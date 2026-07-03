import { useList } from "@refinedev/core";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useSearchParams } from "react-router";
import { CopyButton } from "@/components/copy-button";
import { DataPagination } from "@/components/data-pagination";
import { DetailDialog, DetailRow } from "@/components/detail-dialog";
import { FilterBar, FilterField } from "@/components/filters";
import { PageHeader } from "@/components/page-header";
import { RelativeTime } from "@/components/relative-time";
import { type Column, ResourceTable } from "@/components/resource-table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { apiFetch } from "@/lib/api";
import type {
	ChatRequestLog,
	ChatRequestLogsList,
	ChatRequestStatus,
	KnowledgeBase,
} from "@/types";

const PAGE_SIZE = 25;

const STATUS_VARIANT: Record<
	ChatRequestStatus,
	"default" | "secondary" | "destructive"
> = {
	succeeded: "default",
	pending: "secondary",
	interrupted: "secondary",
	failed: "destructive",
};

const STATUS_OPTIONS = [
	"all",
	"pending",
	"succeeded",
	"failed",
	"interrupted",
] as const;

const ms = (value: number | null): string =>
	value == null ? "—" : `${Math.round(value)} ms`;
const num = (value: number | null): string =>
	value == null ? "—" : String(value);

const columns: Column<ChatRequestLog>[] = [
	{
		header: "Time",
		cell: (log) => <RelativeTime value={log.created_at} />,
	},
	{
		header: "Model",
		cell: (log) => <span className="font-medium">{log.model_public_id}</span>,
	},
	{
		header: "Knowledge base",
		cell: (log) => (
			<span className="text-muted-foreground">
				{log.used_retrieval ? (log.knowledge_base_public_id ?? "—") : "—"}
			</span>
		),
	},
	{
		header: "Status",
		cell: (log) => (
			<Badge
				variant={STATUS_VARIANT[log.status]}
				title={log.error_message ?? undefined}
			>
				{log.status}
			</Badge>
		),
	},
	{ header: "Tokens", cell: (log) => num(log.total_tokens) },
	{ header: "Latency", cell: (log) => ms(log.total_ms) },
	{ header: "Stream", cell: (log) => (log.stream ? "yes" : "no") },
];

export function RequestsList() {
	const [searchParams, setSearchParams] = useSearchParams();
	const [currentPage, setCurrentPage] = useState(1);
	const [model, setModel] = useState("");
	const [status, setStatus] = useState<string>("all");
	const [kbFilter, setKbFilter] = useState("all");
	const [dateFrom, setDateFrom] = useState("");
	const [dateTo, setDateTo] = useState("");
	const [detail, setDetail] = useState<ChatRequestLog | null>(null);

	// A `user_id` query param (e.g. arriving from the Users page) scopes the list to one user.
	const userId = searchParams.get("user_id") ?? "";

	const { result: kbResult } = useList<KnowledgeBase>({
		resource: "knowledge-bases",
		pagination: { currentPage: 1, pageSize: 100 },
	});
	const knowledgeBases = kbResult?.data ?? [];

	const params = new URLSearchParams();
	params.set("limit", String(PAGE_SIZE));
	params.set("offset", String((currentPage - 1) * PAGE_SIZE));
	if (model.trim() !== "") {
		params.set("model", model.trim());
	}
	if (status !== "all") {
		params.set("status", status);
	}
	if (kbFilter !== "all") {
		params.set("knowledge_base_id", kbFilter);
	}
	if (userId !== "") {
		params.set("user_id", userId);
	}
	if (dateFrom !== "") {
		params.set("date_from", new Date(dateFrom).toISOString());
	}
	if (dateTo !== "") {
		params.set("date_to", new Date(dateTo).toISOString());
	}

	const { data, isLoading } = useQuery({
		queryKey: [
			"chat-requests",
			currentPage,
			model,
			status,
			kbFilter,
			userId,
			dateFrom,
			dateTo,
		],
		queryFn: () =>
			apiFetch<ChatRequestLogsList>(
				`/chat-completion-requests?${params.toString()}`,
			),
	});

	const total = data?.total ?? 0;
	const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

	// Any filter change resets to the first page.
	const onFilter = (apply: () => void) => {
		apply();
		setCurrentPage(1);
	};

	const clearUser = () => {
		searchParams.delete("user_id");
		setSearchParams(searchParams);
		setCurrentPage(1);
	};

	const reset = () => {
		setModel("");
		setStatus("all");
		setKbFilter("all");
		setDateFrom("");
		setDateTo("");
		clearUser();
	};

	return (
		<div className="flex flex-col gap-4">
			<PageHeader title="Requests" subtitle={`${total} total`} />

			{userId !== "" ? (
				<div className="flex items-center gap-2 text-sm">
					<span className="text-muted-foreground">Filtered by user</span>
					<Badge variant="secondary" className="font-mono">
						{userId.slice(0, 8)}…
					</Badge>
					<button
						type="button"
						className="text-muted-foreground underline underline-offset-2 hover:text-foreground"
						onClick={clearUser}
					>
						clear
					</button>
				</div>
			) : null}

			<FilterBar onReset={reset}>
				<FilterField label="Model">
					<Input
						value={model}
						onChange={(event) => onFilter(() => setModel(event.target.value))}
						placeholder="model public id"
						className="w-48"
					/>
				</FilterField>
				<FilterField label="Status">
					<Select
						value={status}
						onValueChange={(value) => onFilter(() => setStatus(value))}
					>
						<SelectTrigger className="w-40">
							<SelectValue />
						</SelectTrigger>
						<SelectContent>
							{STATUS_OPTIONS.map((option) => (
								<SelectItem key={option} value={option}>
									{option === "all" ? "All statuses" : option}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</FilterField>
				<FilterField label="Knowledge base">
					<Select
						value={kbFilter}
						onValueChange={(value) => onFilter(() => setKbFilter(value))}
					>
						<SelectTrigger className="w-48">
							<SelectValue />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="all">All knowledge bases</SelectItem>
							{knowledgeBases.map((kb) => (
								<SelectItem key={kb.id} value={kb.id}>
									{kb.public_id}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</FilterField>
				<FilterField label="From">
					<Input
						type="datetime-local"
						value={dateFrom}
						onChange={(event) =>
							onFilter(() => setDateFrom(event.target.value))
						}
					/>
				</FilterField>
				<FilterField label="To">
					<Input
						type="datetime-local"
						value={dateTo}
						onChange={(event) => onFilter(() => setDateTo(event.target.value))}
					/>
				</FilterField>
			</FilterBar>

			<ResourceTable
				columns={columns}
				rows={data?.requests ?? []}
				isLoading={isLoading}
				getRowId={(log) => log.id}
				onRowClick={setDetail}
				emptyLabel="No requests"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
				total={total}
				pageSize={PAGE_SIZE}
			/>

			<RequestDetailDialog
				log={detail}
				onOpenChange={(open) => {
					if (!open) {
						setDetail(null);
					}
				}}
			/>
		</div>
	);
}

function RequestDetailDialog({
	log,
	onOpenChange,
}: {
	log: ChatRequestLog | null;
	onOpenChange: (open: boolean) => void;
}) {
	return (
		<DetailDialog
			open={log !== null}
			onOpenChange={onOpenChange}
			title="Request details"
			description={log ? new Date(log.created_at).toLocaleString() : undefined}
		>
			{log ? (
				<>
					<DetailRow label="Request ID" mono>
						<span className="inline-flex items-center gap-1">
							{log.request_id}
							<CopyButton value={log.request_id} />
						</span>
					</DetailRow>
					{log.completion_id ? (
						<DetailRow label="Completion ID" mono>
							{log.completion_id}
						</DetailRow>
					) : null}
					<DetailRow label="Status">
						<Badge variant={STATUS_VARIANT[log.status]}>{log.status}</Badge>
					</DetailRow>
					{log.error_message || log.error_code ? (
						<DetailRow label="Error">
							<span className="text-destructive">
								{log.error_code ? `[${log.error_code}] ` : ""}
								{log.error_message ?? ""}
							</span>
						</DetailRow>
					) : null}
					<DetailRow label="Model">
						{log.model_public_id}
						{log.provider_model ? (
							<span className="text-muted-foreground">
								{" "}
								({log.provider_model})
							</span>
						) : null}
					</DetailRow>
					<DetailRow label="Provider">{log.provider ?? "—"}</DetailRow>
					<DetailRow label="Retrieval">
						{log.used_retrieval ? (
							<>
								{log.knowledge_base_public_id ?? "—"}
								{log.retrieved_document_ids ? (
									<span className="text-muted-foreground">
										{" "}
										· {log.retrieved_document_ids.length} docs
									</span>
								) : null}
							</>
						) : (
							"not used"
						)}
					</DetailRow>
					<DetailRow label="Stream">{log.stream ? "yes" : "no"}</DetailRow>
					<DetailRow label="Tokens">
						prompt {num(log.prompt_tokens)} · completion{" "}
						{num(log.completion_tokens)} · total {num(log.total_tokens)}
					</DetailRow>
					<DetailRow label="Timings">
						<div className="flex flex-col gap-0.5 text-xs">
							<span>embedding: {ms(log.embedding_ms)}</span>
							<span>qdrant search: {ms(log.qdrant_search_ms)}</span>
							<span>retrieval total: {ms(log.retrieval_total_ms)}</span>
							<span>llm ttfb: {ms(log.llm_ttfb_ms)}</span>
							<span>llm generation: {ms(log.llm_generation_ms)}</span>
							<span className="font-medium">total: {ms(log.total_ms)}</span>
						</div>
					</DetailRow>
					<DetailRow label="Messages">{num(log.messages_count)}</DetailRow>
					<DetailRow label="Query length">{num(log.query_length)}</DetailRow>
					<DetailRow label="Chunks">{num(log.chunks_count)}</DetailRow>
					<DetailRow label="User ID" mono>
						<span className="inline-flex items-center gap-1">
							{log.user_id}
							<CopyButton value={log.user_id} />
						</span>
					</DetailRow>
					<DetailRow label="API key ID" mono>
						{log.api_key_id}
					</DetailRow>
				</>
			) : null}
		</DetailDialog>
	);
}
