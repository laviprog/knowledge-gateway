import type { ReactNode } from "react";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

type DetailDialogProps = {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	title: string;
	description?: ReactNode;
	children: ReactNode;
};

/**
 * Read-only detail view rendered in a scrollable dialog. Pair with `DetailRow` for label/value rows.
 */
export function DetailDialog({
	open,
	onOpenChange,
	title,
	description,
	children,
}: DetailDialogProps) {
	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="max-h-[85vh] gap-4 overflow-y-auto sm:max-w-2xl">
				<DialogHeader>
					<DialogTitle>{title}</DialogTitle>
					{description ? (
						<DialogDescription>{description}</DialogDescription>
					) : null}
				</DialogHeader>
				<div className="flex flex-col">{children}</div>
			</DialogContent>
		</Dialog>
	);
}

type DetailRowProps = {
	label: string;
	children: ReactNode;
	mono?: boolean;
};

export function DetailRow({ label, children, mono }: DetailRowProps) {
	return (
		<div className="grid grid-cols-[150px_1fr] items-start gap-3 border-b py-2 text-sm last:border-0">
			<span className="text-muted-foreground">{label}</span>
			<div className={cn("min-w-0 break-words", mono && "font-mono text-xs")}>
				{children}
			</div>
		</div>
	);
}
