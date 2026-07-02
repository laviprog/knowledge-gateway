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
import type { EmbeddingModel, Provider } from "@/types";

const PAGE_SIZE = 20;
const RESOURCE = "embedding-models";

type EmbeddingForm = {
	public_id: string;
	provider_model: string;
	provider_id: string;
	dimension: string;
	collection_name: string;
	description: string;
};

const EMPTY_FORM: EmbeddingForm = {
	public_id: "",
	provider_model: "",
	provider_id: "",
	dimension: "",
	collection_name: "",
	description: "",
};

const optionalNumber = (value: string): number | undefined =>
	value.trim() === "" ? undefined : Number(value);

const optionalText = (value: string): string | undefined =>
	value.trim() === "" ? undefined : value;

const columns: Column<EmbeddingModel>[] = [
	{
		header: "Public ID",
		cell: (m) => <span className="font-medium">{m.public_id}</span>,
	},
	{ header: "Provider model", cell: (m) => m.provider_model },
	{ header: "Dimension", cell: (m) => m.dimension ?? "—" },
	{
		header: "Collection",
		cell: (m) => (
			<span className="text-muted-foreground">{m.collection_name}</span>
		),
	},
];

export function EmbeddingModelsList() {
	const [currentPage, setCurrentPage] = useState(1);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [editing, setEditing] = useState<EmbeddingModel | null>(null);
	const [form, setForm] = useState<EmbeddingForm>(EMPTY_FORM);
	const [submitting, setSubmitting] = useState(false);

	const { result, query } = useList<EmbeddingModel>({
		resource: RESOURCE,
		pagination: { currentPage, pageSize: PAGE_SIZE },
	});
	const { result: providersResult } = useList<Provider>({
		resource: "providers",
		pagination: { currentPage: 1, pageSize: 100 },
	});
	const { mutate: create } = useCreate();
	const { mutate: update } = useUpdate();
	const { mutate: remove } = useDelete();

	const total = result?.total ?? 0;
	const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));
	const providerOptions = (providersResult?.data ?? []).map((provider) => ({
		value: provider.id,
		label: provider.public_id,
	}));

	const openCreate = () => {
		setEditing(null);
		setForm(EMPTY_FORM);
		setDialogOpen(true);
	};

	const openEdit = (model: EmbeddingModel) => {
		setEditing(model);
		setForm({
			public_id: model.public_id,
			provider_model: model.provider_model,
			provider_id: model.provider_id,
			dimension: model.dimension?.toString() ?? "",
			collection_name: model.collection_name,
			description: model.description ?? "",
		});
		setDialogOpen(true);
	};

	const set = <K extends keyof EmbeddingForm>(
		key: K,
		value: EmbeddingForm[K],
	) => setForm((prev) => ({ ...prev, [key]: value }));

	const onSubmit = () => {
		setSubmitting(true);
		const options = {
			onSuccess: () => setDialogOpen(false),
			onSettled: () => setSubmitting(false),
		};
		if (editing) {
			// collection_name is immutable, so it is omitted from updates.
			update(
				{
					resource: RESOURCE,
					id: editing.id,
					values: {
						public_id: form.public_id,
						provider_model: form.provider_model,
						provider_id: form.provider_id,
						dimension: optionalNumber(form.dimension),
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
						provider_model: form.provider_model,
						provider_id: form.provider_id,
						dimension: optionalNumber(form.dimension),
						collection_name: optionalText(form.collection_name),
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
				title="Embedding models"
				subtitle={`${total} total`}
				actions={<Button onClick={openCreate}>New embedding model</Button>}
			/>

			<ResourceTable
				columns={columns}
				rows={result?.data ?? []}
				isLoading={query.isLoading}
				getRowId={(model) => model.id}
				onEdit={openEdit}
				onDelete={(model) => remove({ resource: RESOURCE, id: model.id })}
				emptyLabel="No embedding models"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
			/>

			<FormDialog
				open={dialogOpen}
				onOpenChange={setDialogOpen}
				title={editing ? "Edit embedding model" : "New embedding model"}
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
					id="provider_model"
					label="Provider model"
					value={form.provider_model}
					onChange={(value) => set("provider_model", value)}
					placeholder="text-embedding-3-small"
					required
				/>
				<SelectField
					id="provider_id"
					label="Provider"
					value={form.provider_id}
					onChange={(value) => set("provider_id", value)}
					options={providerOptions}
				/>
				<TextField
					id="dimension"
					label="Dimension"
					type="number"
					value={form.dimension}
					onChange={(value) => set("dimension", value)}
				/>
				{editing ? null : (
					<TextField
						id="collection_name"
						label="Collection name"
						value={form.collection_name}
						onChange={(value) => set("collection_name", value)}
						hint="Optional — defaults from the public ID. Immutable after creation."
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
