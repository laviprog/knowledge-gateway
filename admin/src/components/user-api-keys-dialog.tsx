import type { HttpError } from "@refinedev/core";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { apiFetch } from "@/lib/api";
import type { ApiKey, ApiKeyCreated } from "@/types";

type UserApiKeysDialogProps = {
	userId: string;
	userName: string;
	open: boolean;
	onOpenChange: (open: boolean) => void;
};

type ApiKeyStatus = "active" | "revoked" | "expired";

function keyStatus(key: ApiKey): ApiKeyStatus {
	if (key.revoked_at) {
		return "revoked";
	}
	if (key.expires_at && new Date(key.expires_at).getTime() < Date.now()) {
		return "expired";
	}
	return "active";
}

const STATUS_VARIANT: Record<
	ApiKeyStatus,
	"default" | "secondary" | "destructive"
> = {
	active: "default",
	revoked: "destructive",
	expired: "secondary",
};

export function UserApiKeysDialog({
	userId,
	userName,
	open,
	onOpenChange,
}: UserApiKeysDialogProps) {
	const queryClient = useQueryClient();
	const queryKey = ["user-api-keys", userId];
	const [name, setName] = useState("");
	const [expiresAt, setExpiresAt] = useState("");
	const [rawKey, setRawKey] = useState<string | null>(null);

	// Reset transient state whenever the dialog is (re)opened.
	useEffect(() => {
		if (open) {
			setRawKey(null);
			setName("");
			setExpiresAt("");
		}
	}, [open]);

	const keysQuery = useQuery({
		queryKey,
		queryFn: () =>
			apiFetch<{ api_keys: ApiKey[] }>(`/users/${userId}/api-keys?limit=100`),
		enabled: open,
	});

	const createMutation = useMutation({
		mutationFn: () =>
			apiFetch<ApiKeyCreated>(`/users/${userId}/api-keys`, {
				method: "POST",
				body: JSON.stringify({
					name: name.trim() === "" ? null : name,
					expires_at:
						expiresAt === "" ? null : new Date(expiresAt).toISOString(),
				}),
			}),
		onSuccess: (created) => {
			setRawKey(created.api_key);
			setName("");
			setExpiresAt("");
			queryClient.invalidateQueries({ queryKey });
			toast.success("API key created");
		},
		onError: (error: HttpError) => toast.error(error.message),
	});

	const revokeMutation = useMutation({
		mutationFn: (keyId: string) =>
			apiFetch<ApiKey>(`/api-keys/${keyId}/revoke`, { method: "POST" }),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey });
			toast.success("API key revoked");
		},
		onError: (error: HttpError) => toast.error(error.message),
	});

	const copyKey = async () => {
		if (rawKey) {
			await navigator.clipboard.writeText(rawKey);
			toast.success("Copied to clipboard");
		}
	};

	const keys = keysQuery.data?.api_keys ?? [];

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-2xl">
				<DialogHeader>
					<DialogTitle>API keys — {userName}</DialogTitle>
					<DialogDescription>
						Issue and revoke API keys. A new key's secret is shown only once.
					</DialogDescription>
				</DialogHeader>

				{rawKey ? (
					<div className="flex flex-col gap-2 rounded-md border border-primary/40 bg-muted p-3">
						<span className="text-sm font-medium">
							New API key (copy it now):
						</span>
						<div className="flex gap-2">
							<Input readOnly value={rawKey} className="font-mono text-xs" />
							<Button
								type="button"
								variant="outline"
								size="icon"
								onClick={copyKey}
							>
								<Copy className="size-4" />
							</Button>
						</div>
					</div>
				) : null}

				<form
					className="flex items-end gap-2"
					onSubmit={(event) => {
						event.preventDefault();
						createMutation.mutate();
					}}
				>
					<div className="flex flex-1 flex-col gap-2">
						<Label htmlFor="key_name">Name (optional)</Label>
						<Input
							id="key_name"
							value={name}
							onChange={(event) => setName(event.target.value)}
							placeholder="e.g. ci-pipeline"
						/>
					</div>
					<div className="flex flex-col gap-2">
						<Label htmlFor="key_expires">Expires (optional)</Label>
						<Input
							id="key_expires"
							type="datetime-local"
							value={expiresAt}
							onChange={(event) => setExpiresAt(event.target.value)}
						/>
					</div>
					<Button type="submit" disabled={createMutation.isPending}>
						Create
					</Button>
				</form>

				<div className="rounded-md border">
					<Table>
						<TableHeader>
							<TableRow>
								<TableHead>Name</TableHead>
								<TableHead>Prefix</TableHead>
								<TableHead>Status</TableHead>
								<TableHead className="w-24 text-right">Actions</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{keysQuery.isLoading ? (
								<TableRow>
									<TableCell
										colSpan={4}
										className="text-center text-muted-foreground"
									>
										Loading…
									</TableCell>
								</TableRow>
							) : keys.length === 0 ? (
								<TableRow>
									<TableCell
										colSpan={4}
										className="text-center text-muted-foreground"
									>
										No API keys
									</TableCell>
								</TableRow>
							) : (
								keys.map((key) => {
									const status = keyStatus(key);
									return (
										<TableRow key={key.id}>
											<TableCell>{key.name ?? "—"}</TableCell>
											<TableCell className="font-mono text-xs">
												{key.key_prefix}…
											</TableCell>
											<TableCell>
												<Badge variant={STATUS_VARIANT[status]}>{status}</Badge>
											</TableCell>
											<TableCell className="text-right">
												<Button
													variant="ghost"
													size="sm"
													disabled={
														status !== "active" || revokeMutation.isPending
													}
													onClick={() => revokeMutation.mutate(key.id)}
												>
													Revoke
												</Button>
											</TableCell>
										</TableRow>
									);
								})
							)}
						</TableBody>
					</Table>
				</div>
			</DialogContent>
		</Dialog>
	);
}
