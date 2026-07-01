import type { FormEvent, ReactNode } from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";

type FormDialogProps = {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	title: string;
	description?: string;
	onSubmit: () => void;
	isPending?: boolean;
	submitLabel?: string;
	children: ReactNode;
};

export function FormDialog({
	open,
	onOpenChange,
	title,
	description,
	onSubmit,
	isPending,
	submitLabel = "Save",
	children,
}: FormDialogProps) {
	const handleSubmit = (event: FormEvent) => {
		event.preventDefault();
		onSubmit();
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent>
				<form onSubmit={handleSubmit} className="flex flex-col gap-4">
					<DialogHeader>
						<DialogTitle>{title}</DialogTitle>
						{description ? (
							<DialogDescription>{description}</DialogDescription>
						) : null}
					</DialogHeader>
					<div className="flex flex-col gap-4">{children}</div>
					<DialogFooter>
						<Button
							type="button"
							variant="outline"
							onClick={() => onOpenChange(false)}
						>
							Cancel
						</Button>
						<Button type="submit" disabled={isPending}>
							{isPending ? "Saving…" : submitLabel}
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
