import type { ReactNode } from "react";

type PageHeaderProps = {
	title: string;
	subtitle?: string;
	actions?: ReactNode;
};

export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
	return (
		<div className="flex items-center justify-between">
			<div>
				<h1 className="text-2xl font-semibold">{title}</h1>
				{subtitle ? (
					<p className="text-sm text-muted-foreground">{subtitle}</p>
				) : null}
			</div>
			{actions ? (
				<div className="flex items-center gap-2">{actions}</div>
			) : null}
		</div>
	);
}
