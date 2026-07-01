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

export type KnowledgeBase = {
	id: string;
	public_id: string;
	name: string;
	embedding_model_id: string;
	description: string | null;
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
