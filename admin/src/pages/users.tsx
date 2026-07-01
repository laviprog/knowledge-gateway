import { useCreate, useDelete, useList, useUpdate } from "@refinedev/core";
import { useState } from "react";
import { DataPagination } from "@/components/data-pagination";
import { FormDialog } from "@/components/form-dialog";
import { SelectField, TextField } from "@/components/form-fields";
import { PageHeader } from "@/components/page-header";
import { type Column, ResourceTable } from "@/components/resource-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Role, User } from "@/types";

const PAGE_SIZE = 20;
const RESOURCE = "users";

type UserForm = {
	name: string;
	role: Role;
	requests_per_minute: string;
};

const EMPTY_FORM: UserForm = {
	name: "",
	role: "user",
	requests_per_minute: "60",
};

const columns: Column<User>[] = [
	{
		header: "Name",
		cell: (user) => <span className="font-medium">{user.name}</span>,
	},
	{
		header: "Role",
		cell: (user) => (
			<Badge variant={user.role === "admin" ? "default" : "secondary"}>
				{user.role}
			</Badge>
		),
	},
	{
		header: "Req/min",
		cell: (user) =>
			user.requests_per_minute === 0 ? "unlimited" : user.requests_per_minute,
	},
];

export function UsersList() {
	const [currentPage, setCurrentPage] = useState(1);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [editing, setEditing] = useState<User | null>(null);
	const [form, setForm] = useState<UserForm>(EMPTY_FORM);
	const [submitting, setSubmitting] = useState(false);

	const { result, query } = useList<User>({
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

	const openEdit = (user: User) => {
		setEditing(user);
		setForm({
			name: user.name,
			role: user.role,
			requests_per_minute: String(user.requests_per_minute),
		});
		setDialogOpen(true);
	};

	const set = <K extends keyof UserForm>(key: K, value: UserForm[K]) =>
		setForm((prev) => ({ ...prev, [key]: value }));

	const onSubmit = () => {
		const values = {
			name: form.name,
			role: form.role,
			requests_per_minute: Number(form.requests_per_minute),
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
				title="Users"
				subtitle={`${total} total`}
				actions={<Button onClick={openCreate}>New user</Button>}
			/>

			<ResourceTable
				columns={columns}
				rows={result?.data ?? []}
				isLoading={query.isLoading}
				getRowId={(user) => user.id}
				onEdit={openEdit}
				onDelete={(user) => remove({ resource: RESOURCE, id: user.id })}
				emptyLabel="No users"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
			/>

			<FormDialog
				open={dialogOpen}
				onOpenChange={setDialogOpen}
				title={editing ? "Edit user" : "New user"}
				onSubmit={onSubmit}
				isPending={submitting}
			>
				<TextField
					id="name"
					label="Name"
					value={form.name}
					onChange={(value) => set("name", value)}
					required
				/>
				<SelectField
					id="role"
					label="Role"
					value={form.role}
					onChange={(value) => set("role", value as Role)}
					options={[
						{ value: "user", label: "user" },
						{ value: "admin", label: "admin" },
					]}
				/>
				<TextField
					id="requests_per_minute"
					label="Requests per minute"
					type="number"
					value={form.requests_per_minute}
					onChange={(value) => set("requests_per_minute", value)}
					hint="0 = unlimited"
				/>
			</FormDialog>
		</div>
	);
}
