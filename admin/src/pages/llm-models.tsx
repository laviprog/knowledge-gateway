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
import type { LlmModel, Provider } from "@/types";

const PAGE_SIZE = 20;
const RESOURCE = "llm-models";

type LlmModelForm = {
	public_id: string;
	provider: string;
	provider_model: string;
	context_window_tokens: string;
	max_completion_tokens: string;
	provider_id: string;
	description: string;
};

const EMPTY_FORM: LlmModelForm = {
	public_id: "",
	provider: "openai",
	provider_model: "",
	context_window_tokens: "",
	max_completion_tokens: "",
	provider_id: "",
	description: "",
};

const optionalText = (value: string): string | undefined =>
	value.trim() === "" ? undefined : value;

const columns: Column<LlmModel>[] = [
	{
		header: "Public ID",
		cell: (m) => <span className="font-medium">{m.public_id}</span>,
	},
	{ header: "Provider", cell: (m) => m.provider },
	{ header: "Provider model", cell: (m) => m.provider_model },
	{ header: "Context", cell: (m) => m.context_window_tokens.toLocaleString() },
	{
		header: "Max completion",
		cell: (m) => m.max_completion_tokens.toLocaleString(),
	},
];

export function LlmModelsList() {
	const [currentPage, setCurrentPage] = useState(1);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [editing, setEditing] = useState<LlmModel | null>(null);
	const [form, setForm] = useState<LlmModelForm>(EMPTY_FORM);
	const [submitting, setSubmitting] = useState(false);

	const { result, query } = useList<LlmModel>({
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

	const openEdit = (model: LlmModel) => {
		setEditing(model);
		setForm({
			public_id: model.public_id,
			provider: model.provider,
			provider_model: model.provider_model,
			context_window_tokens: String(model.context_window_tokens),
			max_completion_tokens: String(model.max_completion_tokens),
			provider_id: model.provider_id,
			description: model.description ?? "",
		});
		setDialogOpen(true);
	};

	const set = <K extends keyof LlmModelForm>(key: K, value: LlmModelForm[K]) =>
		setForm((prev) => ({ ...prev, [key]: value }));

	const onSubmit = () => {
		const values = {
			public_id: form.public_id,
			provider: form.provider,
			provider_model: form.provider_model,
			context_window_tokens: Number(form.context_window_tokens),
			max_completion_tokens: Number(form.max_completion_tokens),
			provider_id: form.provider_id,
			description: optionalText(form.description),
		};
		setSubmitting(true);
		const options = {
			onSuccess: () => setDialogOpen(false),
			onSettled: () => setSubmitting(false),
		};
		if (editing) {
			update({ resource: RESOURCE, id: editing.id, values }, options);
		} else {
			create({ resource: RESOURCE, values }, options);
		}
	};

	return (
		<div className="flex flex-col gap-4">
			<PageHeader
				title="LLM models"
				subtitle={`${total} total`}
				actions={<Button onClick={openCreate}>New LLM model</Button>}
			/>

			<ResourceTable
				columns={columns}
				rows={result?.data ?? []}
				isLoading={query.isLoading}
				getRowId={(model) => model.id}
				onEdit={openEdit}
				onDelete={(model) => remove({ resource: RESOURCE, id: model.id })}
				emptyLabel="No LLM models"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
			/>

			<FormDialog
				open={dialogOpen}
				onOpenChange={setDialogOpen}
				title={editing ? "Edit LLM model" : "New LLM model"}
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
				<div className="grid grid-cols-2 gap-4">
					<TextField
						id="provider"
						label="Provider kind"
						value={form.provider}
						onChange={(value) => set("provider", value)}
						required
					/>
					<TextField
						id="provider_model"
						label="Provider model"
						value={form.provider_model}
						onChange={(value) => set("provider_model", value)}
						placeholder="gpt-4o"
						required
					/>
				</div>
				<SelectField
					id="provider_id"
					label="Provider"
					value={form.provider_id}
					onChange={(value) => set("provider_id", value)}
					options={providerOptions}
				/>
				<div className="grid grid-cols-2 gap-4">
					<TextField
						id="context_window_tokens"
						label="Context window"
						type="number"
						value={form.context_window_tokens}
						onChange={(value) => set("context_window_tokens", value)}
						required
					/>
					<TextField
						id="max_completion_tokens"
						label="Max completion"
						type="number"
						value={form.max_completion_tokens}
						onChange={(value) => set("max_completion_tokens", value)}
						required
					/>
				</div>
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
