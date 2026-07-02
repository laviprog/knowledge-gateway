import { useLogin } from "@refinedev/core";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type LoginVariables = {
	name: string;
	password: string;
};

export function LoginPage() {
	const { mutate: login, isPending } = useLogin<LoginVariables>();
	const [name, setName] = useState("");
	const [password, setPassword] = useState("");

	const onSubmit = (event: React.FormEvent) => {
		event.preventDefault();
		login({ name, password });
	};

	return (
		<div className="flex min-h-svh items-center justify-center bg-muted p-6">
			<Card className="w-full max-w-sm">
				<CardHeader>
					<CardTitle>Knowledge Gateway</CardTitle>
					<CardDescription>Sign in to the admin panel</CardDescription>
				</CardHeader>
				<CardContent>
					<form onSubmit={onSubmit} className="flex flex-col gap-4">
						<div className="flex flex-col gap-2">
							<Label htmlFor="name">Admin name</Label>
							<Input
								id="name"
								value={name}
								onChange={(event) => setName(event.target.value)}
								autoComplete="username"
								required
							/>
						</div>
						<div className="flex flex-col gap-2">
							<Label htmlFor="password">Password</Label>
							<Input
								id="password"
								type="password"
								value={password}
								onChange={(event) => setPassword(event.target.value)}
								autoComplete="current-password"
								required
							/>
						</div>
						<Button type="submit" disabled={isPending} className="mt-2">
							{isPending ? "Signing in…" : "Sign in"}
						</Button>
					</form>
				</CardContent>
			</Card>
		</div>
	);
}
