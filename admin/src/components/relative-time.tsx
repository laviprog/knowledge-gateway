const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });

const DIVISIONS: { amount: number; unit: Intl.RelativeTimeFormatUnit }[] = [
	{ amount: 60, unit: "second" },
	{ amount: 60, unit: "minute" },
	{ amount: 24, unit: "hour" },
	{ amount: 7, unit: "day" },
	{ amount: 4.34524, unit: "week" },
	{ amount: 12, unit: "month" },
	{ amount: Number.POSITIVE_INFINITY, unit: "year" },
];

function formatRelative(date: Date): string {
	let duration = (date.getTime() - Date.now()) / 1000;
	for (const division of DIVISIONS) {
		if (Math.abs(duration) < division.amount) {
			return rtf.format(Math.round(duration), division.unit);
		}
		duration /= division.amount;
	}
	return date.toLocaleString();
}

/**
 * Renders a timestamp as a relative label ("2 hours ago"), with the absolute time in the tooltip.
 */
export function RelativeTime({ value }: { value: string | null }) {
	if (!value) {
		return <span className="text-muted-foreground">—</span>;
	}
	const date = new Date(value);
	return (
		<span
			title={date.toLocaleString()}
			className="whitespace-nowrap text-muted-foreground"
		>
			{formatRelative(date)}
		</span>
	);
}
