import { useCreate, useDelete, useList, useUpdate } from "@refinedev/core";
import { useState } from "react";
import { useNavigate } from "react-router";
import { CopyButton } from "@/components/copy-button";
import { DataPagination } from "@/components/data-pagination";
import { DetailDialog, DetailRow } from "@/components/detail-dialog";
import { FormDialog } from "@/components/form-dialog";
import {
	SelectField,
	TextareaField,
	TextField,
} from "@/components/form-fields";
import { PageHeader } from "@/components/page-header";
import { RelativeTime } from "@/components/relative-time";
import { type Column, ResourceTable } from "@/components/resource-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { EmbeddingModel, KnowledgeBase } from "@/types";

const PAGE_SIZE = 20;
const RESOURCE = "knowledge-bases";

type KnowledgeBaseForm = {
	public_id: string;
	name: string;
	embedding_model_id: string;
	description: string;
	min_score: string;
	system_prompt: string;
};

const EMPTY_FORM: KnowledgeBaseForm = {
	public_id: "",
	name: "",
	embedding_model_id: "",
	description: "",
	min_score: "",
	system_prompt: "",
};

const optionalText = (value: string): string | undefined =>
	value.trim() === "" ? undefined : value;

// Parse the min-score input into a float override, or `undefined` to fall back
// to the global RAG setting. Invalid input is treated as "unset".
const optionalScore = (value: string): number | undefined => {
	const trimmed = value.trim();
	if (trimmed === "") {
		return undefined;
	}
	const parsed = Number(trimmed);
	return Number.isFinite(parsed) ? parsed : undefined;
};

export function KnowledgeBasesList() {
	const [currentPage, setCurrentPage] = useState(1);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [editing, setEditing] = useState<KnowledgeBase | null>(null);
	const [form, setForm] = useState<KnowledgeBaseForm>(EMPTY_FORM);
	const [submitting, setSubmitting] = useState(false);
	const [detail, setDetail] = useState<KnowledgeBase | null>(null);
	const navigate = useNavigate();

	const { result, query } = useList<KnowledgeBase>({
		resource: RESOURCE,
		pagination: { currentPage, pageSize: PAGE_SIZE },
	});
	const { result: embeddingResult } = useList<EmbeddingModel>({
		resource: "embedding-models",
		pagination: { currentPage: 1, pageSize: 100 },
	});
	const { mutate: create } = useCreate();
	const { mutate: update } = useUpdate();
	const { mutate: remove } = useDelete();

	const total = result?.total ?? 0;
	const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

	const embeddingModels = embeddingResult?.data ?? [];
	const embeddingOptions = embeddingModels.map((model) => ({
		value: model.id,
		label: model.public_id,
	}));
	const embeddingLabel = (id: string) =>
		embeddingModels.find((model) => model.id === id)?.public_id ?? id;

	const columns: Column<KnowledgeBase>[] = [
		{
			header: "Public ID",
			cell: (kb) => <span className="font-medium">{kb.public_id}</span>,
		},
		{ header: "Name", cell: (kb) => kb.name },
		{
			header: "Embedding model",
			cell: (kb) => (
				<span className="text-muted-foreground">
					{kb.embedding_model_public_id ??
						embeddingLabel(kb.embedding_model_id)}
				</span>
			),
		},
		{
			header: "Documents",
			cell: (kb) => (
				<span className="text-muted-foreground">
					{kb.document_count}
					{kb.index_status_counts.failed > 0 ? (
						<span className="text-destructive">
							{" "}
							({kb.index_status_counts.failed} failed)
						</span>
					) : null}
				</span>
			),
		},
		{
			header: "Min score",
			cell: (kb) => (
				<span className="text-muted-foreground">
					{kb.min_score == null ? "default" : kb.min_score}
				</span>
			),
		},
	];

	const openCreate = () => {
		setEditing(null);
		setForm(EMPTY_FORM);
		setDialogOpen(true);
	};

	const openEdit = (kb: KnowledgeBase) => {
		setEditing(kb);
		setForm({
			public_id: kb.public_id,
			name: kb.name,
			embedding_model_id: kb.embedding_model_id,
			description: kb.description ?? "",
			min_score: kb.min_score == null ? "" : String(kb.min_score),
			system_prompt: kb.system_prompt ?? "",
		});
		setDialogOpen(true);
	};

	const set = <K extends keyof KnowledgeBaseForm>(
		key: K,
		value: KnowledgeBaseForm[K],
	) => setForm((prev) => ({ ...prev, [key]: value }));

	const onSubmit = () => {
		setSubmitting(true);
		const options = {
			onSuccess: () => setDialogOpen(false),
			onSettled: () => setSubmitting(false),
		};
		if (editing) {
			// embedding_model_id is fixed at creation, so it is omitted from updates.
			update(
				{
					resource: RESOURCE,
					id: editing.id,
					values: {
						public_id: form.public_id,
						name: form.name,
						description: optionalText(form.description),
						min_score: optionalScore(form.min_score) ?? null,
						system_prompt: optionalText(form.system_prompt) ?? null,
					},
				},
				options,
			);
		} else {
			create(
				{
					resource: RESOURCE,
					values: {
						public_id: form.public_id,
						name: form.name,
						embedding_model_id: form.embedding_model_id,
						description: optionalText(form.description),
						min_score: optionalScore(form.min_score),
						system_prompt: optionalText(form.system_prompt),
					},
				},
				options,
			);
		}
	};

	return (
		<div className="flex flex-col gap-4">
			<PageHeader
				title="Knowledge bases"
				subtitle={`${total} total`}
				actions={<Button onClick={openCreate}>New knowledge base</Button>}
			/>

			<ResourceTable
				columns={columns}
				rows={result?.data ?? []}
				isLoading={query.isLoading}
				getRowId={(kb) => kb.id}
				onRowClick={setDetail}
				onEdit={openEdit}
				onDelete={(kb) => remove({ resource: RESOURCE, id: kb.id })}
				getDeleteLabel={(kb) => kb.name}
				emptyLabel="No knowledge bases"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
				total={total}
				pageSize={PAGE_SIZE}
			/>

			<FormDialog
				open={dialogOpen}
				onOpenChange={setDialogOpen}
				title={editing ? "Edit knowledge base" : "New knowledge base"}
				onSubmit={onSubmit}
				isPending={submitting}
			>
				<TextField
					id="public_id"
					label="Public ID"
					value={form.public_id}
					onChange={(value) => set("public_id", value)}
					required
				/>
				<TextField
					id="name"
					label="Name"
					value={form.name}
					onChange={(value) => set("name", value)}
					required
				/>
				{editing ? null : (
					<SelectField
						id="embedding_model_id"
						label="Embedding model"
						value={form.embedding_model_id}
						onChange={(value) => set("embedding_model_id", value)}
						options={embeddingOptions}
					/>
				)}
				<TextareaField
					id="description"
					label="Description"
					value={form.description}
					onChange={(value) => set("description", value)}
				/>
				<TextField
					id="min_score"
					label="Min score"
					type="number"
					value={form.min_score}
					onChange={(value) => set("min_score", value)}
					placeholder="Global default"
					hint="Minimum similarity score (0–1) a chunk must reach to be used as context. Leave empty to use the global default."
				/>
				<TextareaField
					id="system_prompt"
					label="System prompt"
					value={form.system_prompt}
					onChange={(value) => set("system_prompt", value)}
					placeholder="Global default"
				/>
			</FormDialog>

			<DetailDialog
				open={detail !== null}
				onOpenChange={(open) => {
					if (!open) {
						setDetail(null);
					}
				}}
				title={detail?.name ?? "Knowledge base"}
				description={detail?.public_id}
			>
				{detail ? (
					<>
						<DetailRow label="ID" mono>
							<span className="inline-flex items-center gap-1">
								{detail.id}
								<CopyButton value={detail.id} />
							</span>
						</DetailRow>
						<DetailRow label="Embedding model">
							{detail.embedding_model_public_id ??
								embeddingLabel(detail.embedding_model_id)}
						</DetailRow>
						<DetailRow label="Description">
							{detail.description ?? "—"}
						</DetailRow>
						<DetailRow label="Min score">
							{detail.min_score == null ? "global default" : detail.min_score}
						</DetailRow>
						<DetailRow label="System prompt">
							{detail.system_prompt ? (
								<pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded bg-muted p-2 text-xs">
									{detail.system_prompt}
								</pre>
							) : (
								"global default"
							)}
						</DetailRow>
						<DetailRow label="Documents">{detail.document_count}</DetailRow>
						<DetailRow label="Index status">
							<div className="flex flex-wrap gap-1.5">
								<Badge variant="secondary">
									pending: {detail.index_status_counts.pending}
								</Badge>
								<Badge variant="secondary">
									indexing: {detail.index_status_counts.indexing}
								</Badge>
								<Badge variant="default">
									indexed: {detail.index_status_counts.indexed}
								</Badge>
								{detail.index_status_counts.failed > 0 ? (
									<Badge variant="destructive">
										failed: {detail.index_status_counts.failed}
									</Badge>
								) : (
									<Badge variant="secondary">failed: 0</Badge>
								)}
							</div>
						</DetailRow>
						<DetailRow label="Created at">
							<RelativeTime value={detail.created_at} />
						</DetailRow>
						<DetailRow label="Actions">
							<div className="flex gap-2">
								<Button
									variant="outline"
									size="sm"
									onClick={() =>
										navigate(`/documents?knowledge_base_id=${detail.id}`)
									}
								>
									View documents
								</Button>
								<Button
									variant="outline"
									size="sm"
									onClick={() => navigate("/search")}
								>
									Search
								</Button>
							</div>
						</DetailRow>
					</>
				) : null}
			</DetailDialog>
		</div>
	);
}
