import { Check, Copy } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type CopyButtonProps = {
	value: string;
	className?: string;
	label?: string;
};

/**
 * Small ghost icon button that copies `value` to the clipboard and briefly shows a check mark.
 */
export function CopyButton({
	value,
	className,
	label = "Copy",
}: CopyButtonProps) {
	const [copied, setCopied] = useState(false);

	const onCopy = async () => {
		try {
			await navigator.clipboard.writeText(value);
			setCopied(true);
			toast.success("Copied to clipboard");
			setTimeout(() => setCopied(false), 1500);
		} catch {
			toast.error("Failed to copy");
		}
	};

	return (
		<Button
			type="button"
			variant="ghost"
			size="icon-xs"
			className={cn("text-muted-foreground", className)}
			onClick={onCopy}
			title={label}
			aria-label={label}
		>
			{copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
		</Button>
	);
}
