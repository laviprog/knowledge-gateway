import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { DataPagination } from "@/components/data-pagination";
import { FilterBar, FilterField } from "@/components/filters";
import { PageHeader } from "@/components/page-header";
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
		cell: (log) => (
			<span className="whitespace-nowrap text-muted-foreground">
				{new Date(log.created_at).toLocaleString()}
			</span>
		),
	},
	{
		header: "Model",
		cell: (log) => <span className="font-medium">{log.model_public_id}</span>,
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
	const [currentPage, setCurrentPage] = useState(1);
	const [model, setModel] = useState("");
	const [status, setStatus] = useState<string>("all");
	const [dateFrom, setDateFrom] = useState("");
	const [dateTo, setDateTo] = useState("");

	const params = new URLSearchParams();
	params.set("limit", String(PAGE_SIZE));
	params.set("offset", String((currentPage - 1) * PAGE_SIZE));
	if (model.trim() !== "") {
		params.set("model", model.trim());
	}
	if (status !== "all") {
		params.set("status", status);
	}
	if (dateFrom !== "") {
		params.set("date_from", new Date(dateFrom).toISOString());
	}
	if (dateTo !== "") {
		params.set("date_to", new Date(dateTo).toISOString());
	}

	const { data, isLoading } = useQuery({
		queryKey: ["chat-requests", currentPage, model, status, dateFrom, dateTo],
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

	const reset = () => {
		setModel("");
		setStatus("all");
		setDateFrom("");
		setDateTo("");
		setCurrentPage(1);
	};

	return (
		<div className="flex flex-col gap-4">
			<PageHeader title="Requests" subtitle={`${total} total`} />

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
				emptyLabel="No requests"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
			/>
		</div>
	);
}
