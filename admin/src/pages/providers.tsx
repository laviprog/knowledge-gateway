import { useCreate, useDelete, useList, useUpdate } from "@refinedev/core";
import { useState } from "react";
import { DataPagination } from "@/components/data-pagination";
import { FormDialog } from "@/components/form-dialog";
import { TextareaField, TextField } from "@/components/form-fields";
import { PageHeader } from "@/components/page-header";
import { type Column, ResourceTable } from "@/components/resource-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Provider } from "@/types";

const PAGE_SIZE = 20;
const RESOURCE = "providers";

type ProviderForm = {
	public_id: string;
	base_url: string;
	api_key: string;
	timeout_seconds: string;
	max_retries: string;
	description: string;
};

const EMPTY_FORM: ProviderForm = {
	public_id: "",
	base_url: "",
	api_key: "",
	timeout_seconds: "",
	max_retries: "",
	description: "",
};

const optionalNumber = (value: string): number | undefined =>
	value.trim() === "" ? undefined : Number(value);

const optionalText = (value: string): string | undefined =>
	value.trim() === "" ? undefined : value;

const columns: Column<Provider>[] = [
	{
		header: "Public ID",
		cell: (p) => <span className="font-medium">{p.public_id}</span>,
	},
	{
		header: "Base URL",
		cell: (p) => <span className="text-muted-foreground">{p.base_url}</span>,
	},
	{
		header: "API key",
		cell: (p) => (
			<Badge variant={p.has_api_key ? "default" : "secondary"}>
				{p.has_api_key ? "set" : "none"}
			</Badge>
		),
	},
	{ header: "Timeout", cell: (p) => p.timeout_seconds ?? "—" },
	{ header: "Retries", cell: (p) => p.max_retries ?? "—" },
];

export function ProvidersList() {
	const [currentPage, setCurrentPage] = useState(1);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [editing, setEditing] = useState<Provider | null>(null);
	const [form, setForm] = useState<ProviderForm>(EMPTY_FORM);
	const [submitting, setSubmitting] = useState(false);

	const { result, query } = useList<Provider>({
		resource: RESOURCE,
		pagination: { currentPage, pageSize: PAGE_SIZE },
	});
	const { mutate: create } = useCreate();
	const { mutate: update } = useUpdate();
	const { mutate: remove } = useDelete();

	const total = result?.total ?? 0;
	const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

	const openCreate = () => {
		setEditing(null);
		setForm(EMPTY_FORM);
		setDialogOpen(true);
	};

	const openEdit = (provider: Provider) => {
		setEditing(provider);
		setForm({
			public_id: provider.public_id,
			base_url: provider.base_url,
			api_key: "",
			timeout_seconds: provider.timeout_seconds?.toString() ?? "",
			max_retries: provider.max_retries?.toString() ?? "",
			description: provider.description ?? "",
		});
		setDialogOpen(true);
	};

	const set = <K extends keyof ProviderForm>(key: K, value: ProviderForm[K]) =>
		setForm((prev) => ({ ...prev, [key]: value }));

	const onSubmit = () => {
		const values = {
			public_id: form.public_id,
			base_url: form.base_url,
			api_key: optionalText(form.api_key),
			timeout_seconds: optionalNumber(form.timeout_seconds),
			max_retries: optionalNumber(form.max_retries),
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
				title="Providers"
				subtitle={`${total} total`}
				actions={<Button onClick={openCreate}>New provider</Button>}
			/>

			<ResourceTable
				columns={columns}
				rows={result?.data ?? []}
				isLoading={query.isLoading}
				getRowId={(provider) => provider.id}
				onEdit={openEdit}
				onDelete={(provider) => remove({ resource: RESOURCE, id: provider.id })}
				emptyLabel="No providers"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
			/>

			<FormDialog
				open={dialogOpen}
				onOpenChange={setDialogOpen}
				title={editing ? "Edit provider" : "New provider"}
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
					id="base_url"
					label="Base URL"
					value={form.base_url}
					onChange={(value) => set("base_url", value)}
					placeholder="https://api.openai.com/v1"
					required
				/>
				<TextField
					id="api_key"
					label="API key"
					type="password"
					value={form.api_key}
					onChange={(value) => set("api_key", value)}
					hint={editing ? "Leave blank to keep the current key" : "Optional"}
				/>
				<div className="grid grid-cols-2 gap-4">
					<TextField
						id="timeout_seconds"
						label="Timeout (s)"
						type="number"
						value={form.timeout_seconds}
						onChange={(value) => set("timeout_seconds", value)}
					/>
					<TextField
						id="max_retries"
						label="Max retries"
						type="number"
						value={form.max_retries}
						onChange={(value) => set("max_retries", value)}
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
