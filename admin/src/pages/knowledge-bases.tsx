import { useCreate, useDelete, useList, useUpdate } from "@refinedev/core";
import { useState } from "react";
import { DataPagination } from "@/components/data-pagination";
import { FormDialog } from "@/components/form-dialog";
import {
	SelectField,
	TextareaField,
	TextField,
} from "@/components/form-fields";
import { PageHeader } from "@/components/page-header";
import { type Column, ResourceTable } from "@/components/resource-table";
import { Button } from "@/components/ui/button";
import type { EmbeddingModel, KnowledgeBase } from "@/types";

const PAGE_SIZE = 20;
const RESOURCE = "knowledge-bases";

type KnowledgeBaseForm = {
	public_id: string;
	name: string;
	embedding_model_id: string;
	description: string;
};

const EMPTY_FORM: KnowledgeBaseForm = {
	public_id: "",
	name: "",
	embedding_model_id: "",
	description: "",
};

const optionalText = (value: string): string | undefined =>
	value.trim() === "" ? undefined : value;

export function KnowledgeBasesList() {
	const [currentPage, setCurrentPage] = useState(1);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [editing, setEditing] = useState<KnowledgeBase | null>(null);
	const [form, setForm] = useState<KnowledgeBaseForm>(EMPTY_FORM);
	const [submitting, setSubmitting] = useState(false);

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
					{embeddingLabel(kb.embedding_model_id)}
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
				onEdit={openEdit}
				onDelete={(kb) => remove({ resource: RESOURCE, id: kb.id })}
				emptyLabel="No knowledge bases"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
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
			</FormDialog>
		</div>
	);
}
