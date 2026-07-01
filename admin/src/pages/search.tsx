import type { HttpError } from "@refinedev/core";
import { useList } from "@refinedev/core";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { SelectField, TextField } from "@/components/form-fields";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiFetch } from "@/lib/api";
import type { DocumentSearchResults, KnowledgeBase } from "@/types";

export function SearchPage() {
	const [knowledgeBaseId, setKnowledgeBaseId] = useState("");
	const [queryText, setQueryText] = useState("");
	const [limit, setLimit] = useState("5");

	const { result: kbResult } = useList<KnowledgeBase>({
		resource: "knowledge-bases",
		pagination: { currentPage: 1, pageSize: 100 },
	});
	const kbOptions = (kbResult?.data ?? []).map((kb) => ({
		value: kb.id,
		label: kb.public_id,
	}));

	const search = useMutation({
		mutationFn: () =>
			apiFetch<DocumentSearchResults>("/documents/search", {
				method: "POST",
				body: JSON.stringify({
					knowledge_base_id: knowledgeBaseId,
					query: queryText,
					limit: Number(limit),
				}),
			}),
		onError: (error: HttpError) => toast.error(error.message),
	});

	const onSubmit = (event: React.FormEvent) => {
		event.preventDefault();
		if (knowledgeBaseId === "" || queryText.trim() === "") {
			toast.error("Select a knowledge base and enter a query");
			return;
		}
		search.mutate();
	};

	const results = search.data?.results ?? [];

	return (
		<div className="flex flex-col gap-6">
			<PageHeader
				title="Search"
				subtitle="Semantic search over a knowledge base"
			/>

			<form
				onSubmit={onSubmit}
				className="flex flex-col gap-4 rounded-md border bg-card p-4"
			>
				<div className="grid gap-4 sm:grid-cols-[1fr_120px]">
					<SelectField
						id="knowledge_base_id"
						label="Knowledge base"
						value={knowledgeBaseId}
						onChange={setKnowledgeBaseId}
						options={kbOptions}
					/>
					<TextField
						id="limit"
						label="Limit"
						type="number"
						value={limit}
						onChange={setLimit}
						hint="1–20"
					/>
				</div>
				<div className="flex flex-col gap-2">
					<Label htmlFor="query">Query</Label>
					<Textarea
						id="query"
						value={queryText}
						onChange={(event) => setQueryText(event.target.value)}
						placeholder="What are you looking for?"
						rows={3}
					/>
				</div>
				<div>
					<Button type="submit" disabled={search.isPending}>
						{search.isPending ? "Searching…" : "Search"}
					</Button>
				</div>
			</form>

			{search.isSuccess ? (
				<div className="flex flex-col gap-3">
					<h2 className="text-lg font-semibold">
						Results{" "}
						<span className="text-muted-foreground">({results.length})</span>
					</h2>
					{results.length === 0 ? (
						<p className="text-sm text-muted-foreground">No matching chunks</p>
					) : (
						results.map((result) => (
							<Card key={result.chunk_id}>
								<CardHeader className="flex flex-row items-center justify-between gap-2 pb-2">
									<Badge variant="secondary">
										score {result.score.toFixed(3)}
									</Badge>
									<span className="font-mono text-xs text-muted-foreground">
										doc {result.document_id.slice(0, 8)}… · chunk #
										{result.chunk_index}
									</span>
								</CardHeader>
								<CardContent>
									<p className="whitespace-pre-wrap text-sm">
										{result.content}
									</p>
								</CardContent>
							</Card>
						))
					)}
				</div>
			) : null}
		</div>
	);
}
