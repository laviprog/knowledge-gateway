import type { HttpError } from "@refinedev/core";
import { useDelete, useInvalidate, useList } from "@refinedev/core";
import { useState } from "react";
import { useSearchParams } from "react-router";
import { toast } from "sonner";
import { CopyButton } from "@/components/copy-button";
import { DataPagination } from "@/components/data-pagination";
import { DetailDialog, DetailRow } from "@/components/detail-dialog";
import { FilterBar, FilterField } from "@/components/filters";
import { FormDialog } from "@/components/form-dialog";
import { SelectField } from "@/components/form-fields";
import { PageHeader } from "@/components/page-header";
import { RelativeTime } from "@/components/relative-time";
import { type Column, ResourceTable } from "@/components/resource-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { apiUpload } from "@/lib/api";
import type { DocumentIndexStatus, DocumentItem, KnowledgeBase } from "@/types";

const PAGE_SIZE = 20;
const RESOURCE = "documents";

const STATUS_VARIANT: Record<
	DocumentIndexStatus,
	"default" | "secondary" | "destructive"
> = {
	indexed: "default",
	pending: "secondary",
	indexing: "secondary",
	failed: "destructive",
};

export function DocumentsList() {
	const [searchParams] = useSearchParams();
	const [currentPage, setCurrentPage] = useState(1);
	const [uploadOpen, setUploadOpen] = useState(false);
	const [knowledgeBaseId, setKnowledgeBaseId] = useState("");
	// A `knowledge_base_id` query param (e.g. from a knowledge base's detail view) pre-selects
	// the filter.
	const [filterKbId, setFilterKbId] = useState(
		searchParams.get("knowledge_base_id") ?? "all",
	);
	const [detail, setDetail] = useState<DocumentItem | null>(null);
	const [file, setFile] = useState<File | null>(null);
	const [uploading, setUploading] = useState(false);

	const { result, query } = useList<DocumentItem>({
		resource: RESOURCE,
		pagination: { currentPage, pageSize: PAGE_SIZE },
		filters:
			filterKbId === "all"
				? undefined
				: [
						{
							field: "knowledge_base_id",
							operator: "eq",
							value: filterKbId,
						},
					],
	});
	const { result: kbResult } = useList<KnowledgeBase>({
		resource: "knowledge-bases",
		pagination: { currentPage: 1, pageSize: 100 },
	});
	const { mutate: remove } = useDelete();
	const invalidate = useInvalidate();

	const total = result?.total ?? 0;
	const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

	const knowledgeBases = kbResult?.data ?? [];
	const kbOptions = knowledgeBases.map((kb) => ({
		value: kb.id,
		label: kb.public_id,
	}));
	const kbLabel = (id: string) =>
		knowledgeBases.find((kb) => kb.id === id)?.public_id ?? id;

	const columns: Column<DocumentItem>[] = [
		{
			header: "Title",
			cell: (doc) => <span className="font-medium">{doc.title}</span>,
		},
		{
			header: "Knowledge base",
			cell: (doc) => (
				<span className="text-muted-foreground">
					{kbLabel(doc.knowledge_base_id)}
				</span>
			),
		},
		{
			header: "Status",
			cell: (doc) => (
				<Badge
					variant={STATUS_VARIANT[doc.index_status]}
					title={doc.index_error ?? undefined}
				>
					{doc.index_status}
				</Badge>
			),
		},
		{ header: "Chunks", cell: (doc) => doc.chunks_count },
		{
			header: "Indexed",
			cell: (doc) => <RelativeTime value={doc.indexed_at} />,
		},
	];

	const openUpload = () => {
		setKnowledgeBaseId("");
		setFile(null);
		setUploadOpen(true);
	};

	const onUpload = () => {
		if (!file || knowledgeBaseId === "") {
			toast.error("Select a knowledge base and a file");
			return;
		}
		const formData = new FormData();
		formData.append("knowledge_base_id", knowledgeBaseId);
		formData.append("file", file);

		setUploading(true);
		apiUpload("/documents/upload", formData)
			.then(() => {
				toast.success("Document uploaded; indexing started");
				setUploadOpen(false);
				invalidate({ resource: RESOURCE, invalidates: ["list"] });
			})
			.catch((error: HttpError) => toast.error(error.message))
			.finally(() => setUploading(false));
	};

	return (
		<div className="flex flex-col gap-4">
			<PageHeader
				title="Documents"
				subtitle={`${total} total`}
				actions={<Button onClick={openUpload}>Upload document</Button>}
			/>

			<FilterBar
				onReset={
					filterKbId === "all"
						? undefined
						: () => {
								setFilterKbId("all");
								setCurrentPage(1);
							}
				}
			>
				<FilterField label="Knowledge base">
					<Select
						value={filterKbId}
						onValueChange={(value) => {
							setFilterKbId(value);
							setCurrentPage(1);
						}}
					>
						<SelectTrigger className="w-56">
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
			</FilterBar>

			<ResourceTable
				columns={columns}
				rows={result?.data ?? []}
				isLoading={query.isLoading}
				getRowId={(doc) => doc.id}
				onRowClick={setDetail}
				onDelete={(doc) => remove({ resource: RESOURCE, id: doc.id })}
				getDeleteLabel={(doc) => doc.title}
				emptyLabel="No documents"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
				total={total}
				pageSize={PAGE_SIZE}
			/>

			<FormDialog
				open={uploadOpen}
				onOpenChange={setUploadOpen}
				title="Upload document"
				description="Supported files: .txt, .md, .docx, .pdf"
				onSubmit={onUpload}
				isPending={uploading}
				submitLabel="Upload"
			>
				<SelectField
					id="knowledge_base_id"
					label="Knowledge base"
					value={knowledgeBaseId}
					onChange={setKnowledgeBaseId}
					options={kbOptions}
				/>
				<div className="flex flex-col gap-2">
					<Label htmlFor="file">File</Label>
					<Input
						id="file"
						type="file"
						accept=".txt,.md,.docx,.pdf"
						onChange={(event) => setFile(event.target.files?.[0] ?? null)}
					/>
				</div>
			</FormDialog>

			<DetailDialog
				open={detail !== null}
				onOpenChange={(open) => {
					if (!open) {
						setDetail(null);
					}
				}}
				title={detail?.title ?? "Document"}
				description="Document details and indexing status"
			>
				{detail ? (
					<>
						<DetailRow label="ID" mono>
							<span className="inline-flex items-center gap-1">
								{detail.id}
								<CopyButton value={detail.id} />
							</span>
						</DetailRow>
						<DetailRow label="Knowledge base">
							{kbLabel(detail.knowledge_base_id)}
						</DetailRow>
						<DetailRow label="Status">
							<Badge
								variant={STATUS_VARIANT[detail.index_status]}
								className="capitalize"
							>
								{detail.index_status}
							</Badge>
						</DetailRow>
						{detail.index_error ? (
							<DetailRow label="Index error">
								<span className="text-destructive">{detail.index_error}</span>
							</DetailRow>
						) : null}
						<DetailRow label="Chunks">{detail.chunks_count}</DetailRow>
						<DetailRow label="Source">{detail.source ?? "—"}</DetailRow>
						<DetailRow label="Content hash" mono>
							{detail.content_hash}
						</DetailRow>
						<DetailRow label="Indexed at">
							<RelativeTime value={detail.indexed_at} />
						</DetailRow>
						<DetailRow label="Created at">
							<RelativeTime value={detail.created_at} />
						</DetailRow>
						{Object.keys(detail.source_metadata).length > 0 ? (
							<DetailRow label="Metadata" mono>
								<pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded bg-muted p-2">
									{JSON.stringify(detail.source_metadata, null, 2)}
								</pre>
							</DetailRow>
						) : null}
						<DetailRow label="Content">
							<pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded bg-muted p-2 text-xs">
								{detail.content}
							</pre>
						</DetailRow>
					</>
				) : null}
			</DetailDialog>
		</div>
	);
}
