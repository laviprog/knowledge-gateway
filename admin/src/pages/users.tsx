import { useDelete, useList } from "@refinedev/core";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import type { User } from "@/types";

const PAGE_SIZE = 20;

export function UsersList() {
	const [currentPage, setCurrentPage] = useState(1);
	const { result, query } = useList<User>({
		resource: "users",
		pagination: { currentPage, pageSize: PAGE_SIZE },
	});
	const { mutate: remove } = useDelete();

	const isLoading = query.isLoading;
	const users = result?.data ?? [];
	const total = result?.total ?? 0;
	const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

	return (
		<div className="flex flex-col gap-4">
			<div className="flex items-center justify-between">
				<h1 className="text-2xl font-semibold">Users</h1>
				<span className="text-sm text-muted-foreground">{total} total</span>
			</div>

			<div className="rounded-md border">
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead>Name</TableHead>
							<TableHead>Role</TableHead>
							<TableHead>Req/min</TableHead>
							<TableHead className="w-24" />
						</TableRow>
					</TableHeader>
					<TableBody>
						{isLoading ? (
							<TableRow>
								<TableCell
									colSpan={4}
									className="text-center text-muted-foreground"
								>
									Loading…
								</TableCell>
							</TableRow>
						) : users.length === 0 ? (
							<TableRow>
								<TableCell
									colSpan={4}
									className="text-center text-muted-foreground"
								>
									No users
								</TableCell>
							</TableRow>
						) : (
							users.map((user) => (
								<TableRow key={user.id}>
									<TableCell className="font-medium">{user.name}</TableCell>
									<TableCell>
										<Badge
											variant={user.role === "admin" ? "default" : "secondary"}
										>
											{user.role}
										</Badge>
									</TableCell>
									<TableCell>
										{user.requests_per_minute === 0
											? "unlimited"
											: user.requests_per_minute}
									</TableCell>
									<TableCell>
										<Button
											variant="ghost"
											size="sm"
											onClick={() => remove({ resource: "users", id: user.id })}
										>
											Delete
										</Button>
									</TableCell>
								</TableRow>
							))
						)}
					</TableBody>
				</Table>
			</div>

			<div className="flex items-center justify-end gap-2">
				<Button
					variant="outline"
					size="sm"
					disabled={currentPage <= 1}
					onClick={() => setCurrentPage((page) => page - 1)}
				>
					Previous
				</Button>
				<span className="text-sm text-muted-foreground">
					Page {currentPage} / {pageCount}
				</span>
				<Button
					variant="outline"
					size="sm"
					disabled={currentPage >= pageCount}
					onClick={() => setCurrentPage((page) => page + 1)}
				>
					Next
				</Button>
			</div>
		</div>
	);
}
