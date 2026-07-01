import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";

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
	emptyLabel?: string;
};

export function ResourceTable<T>({
	columns,
	rows,
	isLoading,
	getRowId,
	onEdit,
	onDelete,
	emptyLabel = "No records",
}: ResourceTableProps<T>) {
	const hasActions = Boolean(onEdit || onDelete);
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
							<TableHead className="w-32 text-right">Actions</TableHead>
						) : null}
					</TableRow>
				</TableHeader>
				<TableBody>
					{isLoading ? (
						<TableRow>
							<TableCell
								colSpan={colSpan}
								className="text-center text-muted-foreground"
							>
								Loading…
							</TableCell>
						</TableRow>
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
							<TableRow key={getRowId(row)}>
								{columns.map((column) => (
									<TableCell key={column.header} className={column.className}>
										{column.cell(row)}
									</TableCell>
								))}
								{hasActions ? (
									<TableCell className="text-right">
										<div className="flex justify-end gap-1">
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
													onClick={() => onDelete(row)}
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
		</div>
	);
}
