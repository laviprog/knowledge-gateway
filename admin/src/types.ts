export type Role = "admin" | "user";

export type SessionUser = {
	id: string;
	name: string;
	role: Role;
};

type Timestamps = {
	deleted_at: string | null;
	created_at: string;
	updated_at: string;
};

export type User = {
	id: string;
	name: string;
	role: Role;
	requests_per_minute: number;
} & Timestamps;

export type Provider = {
	id: string;
	public_id: string;
	base_url: string;
	has_api_key: boolean;
	timeout_seconds: number | null;
	max_retries: number | null;
	description: string | null;
} & Timestamps;

export type EmbeddingModel = {
	id: string;
	public_id: string;
	provider_model: string;
	dimension: number | null;
	collection_name: string;
	provider_id: string;
	description: string | null;
} & Timestamps;

export type KnowledgeBaseIndexStatusCounts = {
	pending: number;
	indexing: number;
	indexed: number;
	failed: number;
};

export type KnowledgeBase = {
	id: string;
	public_id: string;
	name: string;
	embedding_model_id: string;
	embedding_model_public_id: string | null;
	description: string | null;
	min_score: number | null;
	system_prompt: string | null;
	document_count: number;
	index_status_counts: KnowledgeBaseIndexStatusCounts;
} & Timestamps;

export type LlmModel = {
	id: string;
	public_id: string;
	provider: string;
	provider_model: string;
	context_window_tokens: number;
	max_completion_tokens: number;
	provider_id: string;
	description: string | null;
} & Timestamps;

export type ApiKey = {
	id: string;
	name: string | null;
	key_prefix: string;
	user_id: string;
	revoked_at: string | null;
	expires_at: string | null;
	last_used_at: string | null;
} & Timestamps;

export type ApiKeyCreated = {
	api_key: string;
	api_key_info: ApiKey;
};

export type DocumentIndexStatus = "pending" | "indexing" | "indexed" | "failed";

export type DocumentItem = {
	id: string;
	knowledge_base_id: string;
	title: string;
	content: string;
	content_hash: string;
	source: string | null;
	source_metadata: Record<string, unknown>;
	chunks_count: number;
	index_status: DocumentIndexStatus;
	index_error: string | null;
	indexed_at: string | null;
} & Timestamps;

export type ChatRequestStatus =
	| "pending"
	| "succeeded"
	| "failed"
	| "interrupted";

export type ChatStatusCount = {
	status: ChatRequestStatus;
	count: number;
};

export type ChatModelStats = {
	model_public_id: string;
	requests: number;
	total_tokens: number | null;
	avg_total_ms: number | null;
};

export type ChatKnowledgeBaseStats = {
	knowledge_base_id: string | null;
	knowledge_base_public_id: string | null;
	requests: number;
};

export type ChatCompletionStats = {
	total_requests: number;
	retrieval_requests: number;
	by_status: ChatStatusCount[];
	prompt_tokens_total: number | null;
	completion_tokens_total: number | null;
	total_tokens_total: number | null;
	avg_embedding_ms: number | null;
	avg_llm_ttfb_ms: number | null;
	avg_llm_generation_ms: number | null;
	avg_total_ms: number | null;
	by_model: ChatModelStats[];
	by_knowledge_base: ChatKnowledgeBaseStats[];
};

export type ChatRequestLog = {
	id: string;
	request_id: string;
	user_id: string;
	api_key_id: string;
	model_id: string | null;
	model_public_id: string;
	provider: string | null;
	provider_model: string | null;
	knowledge_base_id: string | null;
	knowledge_base_public_id: string | null;
	used_retrieval: boolean;
	retrieved_document_ids: string[] | null;
	completion_id: string | null;
	stream: boolean;
	status: ChatRequestStatus;
	error_code: string | null;
	error_message: string | null;
	prompt_tokens: number | null;
	completion_tokens: number | null;
	total_tokens: number | null;
	chunks_count: number | null;
	retrieval_total_ms: number | null;
	embedding_ms: number | null;
	qdrant_search_ms: number | null;
	llm_ttfb_ms: number | null;
	llm_generation_ms: number | null;
	total_ms: number | null;
	messages_count: number | null;
	query_length: number | null;
	created_at: string;
	updated_at: string;
};

export type ChatRequestLogsList = {
	requests: ChatRequestLog[];
	total: number;
	limit: number;
	offset: number;
};

export type DocumentSearchResult = {
	score: number;
	document_id: string;
	chunk_id: string;
	chunk_index: number;
	content: string;
};

export type DocumentSearchResults = {
	results: DocumentSearchResult[];
};
