import { Button } from "@/components/ui/button";

type DataPaginationProps = {
	currentPage: number;
	pageCount: number;
	onPageChange: (page: number) => void;
};

export function DataPagination({
	currentPage,
	pageCount,
	onPageChange,
}: DataPaginationProps) {
	return (
		<div className="flex items-center justify-end gap-2">
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
	);
}
