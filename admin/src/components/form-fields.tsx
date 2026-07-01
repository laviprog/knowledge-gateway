import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

type TextFieldProps = {
	id: string;
	label: string;
	value: string;
	onChange: (value: string) => void;
	type?: "text" | "password" | "number";
	placeholder?: string;
	required?: boolean;
	hint?: string;
};

export function TextField({
	id,
	label,
	value,
	onChange,
	type = "text",
	placeholder,
	required,
	hint,
}: TextFieldProps) {
	return (
		<div className="flex flex-col gap-2">
			<Label htmlFor={id}>{label}</Label>
			<Input
				id={id}
				type={type}
				value={value}
				placeholder={placeholder}
				required={required}
				onChange={(event) => onChange(event.target.value)}
			/>
			{hint ? <p className="text-xs text-muted-foreground">{hint}</p> : null}
		</div>
	);
}

type TextareaFieldProps = {
	id: string;
	label: string;
	value: string;
	onChange: (value: string) => void;
	placeholder?: string;
};

export function TextareaField({
	id,
	label,
	value,
	onChange,
	placeholder,
}: TextareaFieldProps) {
	return (
		<div className="flex flex-col gap-2">
			<Label htmlFor={id}>{label}</Label>
			<Textarea
				id={id}
				value={value}
				placeholder={placeholder}
				onChange={(event) => onChange(event.target.value)}
			/>
		</div>
	);
}

export type SelectOption = {
	value: string;
	label: string;
};

type SelectFieldProps = {
	id: string;
	label: string;
	value: string;
	onChange: (value: string) => void;
	options: SelectOption[];
	placeholder?: string;
	disabled?: boolean;
};

export function SelectField({
	id,
	label,
	value,
	onChange,
	options,
	placeholder = "Select…",
	disabled,
}: SelectFieldProps) {
	return (
		<div className="flex flex-col gap-2">
			<Label htmlFor={id}>{label}</Label>
			<Select value={value} onValueChange={onChange} disabled={disabled}>
				<SelectTrigger id={id}>
					<SelectValue placeholder={placeholder} />
				</SelectTrigger>
				<SelectContent>
					{options.map((option) => (
						<SelectItem key={option.value} value={option.value}>
							{option.label}
						</SelectItem>
					))}
				</SelectContent>
			</Select>
		</div>
	);
}
