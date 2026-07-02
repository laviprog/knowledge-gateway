import type { HttpError } from "@refinedev/core";
import { useDelete, useInvalidate, useList } from "@refinedev/core";
import { useState } from "react";
import { toast } from "sonner";
import { DataPagination } from "@/components/data-pagination";
import { FormDialog } from "@/components/form-dialog";
import { SelectField } from "@/components/form-fields";
import { PageHeader } from "@/components/page-header";
import { type Column, ResourceTable } from "@/components/resource-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
	const [currentPage, setCurrentPage] = useState(1);
	const [uploadOpen, setUploadOpen] = useState(false);
	const [knowledgeBaseId, setKnowledgeBaseId] = useState("");
	const [file, setFile] = useState<File | null>(null);
	const [uploading, setUploading] = useState(false);

	const { result, query } = useList<DocumentItem>({
		resource: RESOURCE,
		pagination: { currentPage, pageSize: PAGE_SIZE },
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

			<ResourceTable
				columns={columns}
				rows={result?.data ?? []}
				isLoading={query.isLoading}
				getRowId={(doc) => doc.id}
				onDelete={(doc) => remove({ resource: RESOURCE, id: doc.id })}
				emptyLabel="No documents"
			/>

			<DataPagination
				currentPage={currentPage}
				pageCount={pageCount}
				onPageChange={setCurrentPage}
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
		</div>
	);
}
