import { type ReactNode, useState } from "react";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

export type Column<T> = {
	header: string;
	cell: (row: T) => ReactNode;
	className?: string;
};

type ResourceTableProps<T> = {
	columns: Column<T>[];
	rows: T[];
	isLoading: boolean;
	getRowId: (row: T) => string;
	onEdit?: (row: T) => void;
	onDelete?: (row: T) => void;
	onRowClick?: (row: T) => void;
	extraActions?: (row: T) => ReactNode;
	emptyLabel?: string;
	// Label used in the delete-confirmation prompt, e.g. the row's name.
	getDeleteLabel?: (row: T) => string;
};

const SKELETON_ROWS = 5;

export function ResourceTable<T>({
	columns,
	rows,
	isLoading,
	getRowId,
	onEdit,
	onDelete,
	onRowClick,
	extraActions,
	emptyLabel = "No records",
	getDeleteLabel,
}: ResourceTableProps<T>) {
	const [deleting, setDeleting] = useState<T | null>(null);
	const hasActions = Boolean(onEdit || onDelete || extraActions);
	const colSpan = columns.length + (hasActions ? 1 : 0);

	return (
		<div className="rounded-md border">
			<Table>
				<TableHeader>
					<TableRow>
						{columns.map((column) => (
							<TableHead key={column.header} className={column.className}>
								{column.header}
							</TableHead>
						))}
						{hasActions ? (
							<TableHead className="w-40 text-right">Actions</TableHead>
						) : null}
					</TableRow>
				</TableHeader>
				<TableBody>
					{isLoading ? (
						Array.from({ length: SKELETON_ROWS }).map((_, rowIndex) => (
							// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton placeholder
							<TableRow key={`skeleton-${rowIndex}`}>
								{Array.from({ length: colSpan }).map((__, cellIndex) => (
									<TableCell
										// biome-ignore lint/suspicious/noArrayIndexKey: static skeleton placeholder
										key={`skeleton-cell-${cellIndex}`}
									>
										<Skeleton className="h-4 w-full max-w-32" />
									</TableCell>
								))}
							</TableRow>
						))
					) : rows.length === 0 ? (
						<TableRow>
							<TableCell
								colSpan={colSpan}
								className="text-center text-muted-foreground"
							>
								{emptyLabel}
							</TableCell>
						</TableRow>
					) : (
						rows.map((row) => (
							<TableRow
								key={getRowId(row)}
								onClick={onRowClick ? () => onRowClick(row) : undefined}
								className={cn(onRowClick && "cursor-pointer")}
							>
								{columns.map((column) => (
									<TableCell key={column.header} className={column.className}>
										{column.cell(row)}
									</TableCell>
								))}
								{hasActions ? (
									<TableCell className="text-right">
										{/* Stop row-click from firing when interacting with actions. */}
										{/* biome-ignore lint/a11y/noStaticElementInteractions: propagation guard, not a control */}
										<div
											className="flex justify-end gap-1"
											onClick={(event) => event.stopPropagation()}
											onKeyDown={(event) => event.stopPropagation()}
										>
											{extraActions?.(row)}
											{onEdit ? (
												<Button
													variant="ghost"
													size="sm"
													onClick={() => onEdit(row)}
												>
													Edit
												</Button>
											) : null}
											{onDelete ? (
												<Button
													variant="ghost"
													size="sm"
													onClick={() => setDeleting(row)}
												>
													Delete
												</Button>
											) : null}
										</div>
									</TableCell>
								) : null}
							</TableRow>
						))
					)}
				</TableBody>
			</Table>

			<ConfirmDialog
				open={deleting !== null}
				onOpenChange={(open) => {
					if (!open) {
						setDeleting(null);
					}
				}}
				title="Delete this item?"
				description={
					deleting && getDeleteLabel
						? `“${getDeleteLabel(deleting)}” will be permanently deleted. This action cannot be undone.`
						: "This item will be permanently deleted. This action cannot be undone."
				}
				confirmLabel="Delete"
				onConfirm={() => {
					if (deleting && onDelete) {
						onDelete(deleting);
					}
					setDeleting(null);
				}}
			/>
		</div>
	);
}
