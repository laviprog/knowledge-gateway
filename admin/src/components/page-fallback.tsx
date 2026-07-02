import { Loader2 } from "lucide-react";

export function PageFallback() {
	return (
		<div className="flex min-h-64 items-center justify-center text-muted-foreground">
			<Loader2 className="size-6 animate-spin" />
		</div>
	);
}
