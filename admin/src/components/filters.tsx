import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";

export function FilterBar({
	children,
	onReset,
}: {
	children: ReactNode;
	onReset?: () => void;
}) {
	return (
		<div className="flex flex-wrap items-end gap-3 rounded-md border bg-card p-3">
			{children}
			{onReset ? (
				<Button variant="ghost" size="sm" onClick={onReset}>
					Reset
				</Button>
			) : null}
		</div>
	);
}

export function FilterField({
	label,
	children,
}: {
	label: string;
	children: ReactNode;
}) {
	return (
		<div className="flex flex-col gap-1">
			<span className="text-xs text-muted-foreground">{label}</span>
			{children}
		</div>
	);
}
