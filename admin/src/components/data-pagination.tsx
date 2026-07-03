import { Button } from "@/components/ui/button";

type DataPaginationProps = {
	currentPage: number;
	pageCount: number;
	onPageChange: (page: number) => void;
	// When provided, a "start–end of total" range is shown alongside the page indicator.
	total?: number;
	pageSize?: number;
};

export function DataPagination({
	currentPage,
	pageCount,
	onPageChange,
	total,
	pageSize,
}: DataPaginationProps) {
	const range =
		total != null && pageSize != null
			? total === 0
				? "0 of 0"
				: `${(currentPage - 1) * pageSize + 1}–${Math.min(
						currentPage * pageSize,
						total,
					)} of ${total}`
			: null;

	return (
		<div className="flex items-center justify-between gap-2">
			<span className="text-sm text-muted-foreground">{range}</span>
			<div className="flex items-center gap-2">
				<Button
					variant="outline"
					size="sm"
					disabled={currentPage <= 1}
					onClick={() => onPageChange(currentPage - 1)}
				>
					Previous
				</Button>
				<span className="text-sm text-muted-foreground">
					Page {currentPage} / {pageCount}
				</span>
				<Button
					variant="outline"
					size="sm"
					disabled={currentPage >= pageCount}
					onClick={() => onPageChange(currentPage + 1)}
				>
					Next
				</Button>
			</div>
		</div>
	);
}
