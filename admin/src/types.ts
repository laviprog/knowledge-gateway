export type Role = "admin" | "user";

export type SessionUser = {
	id: string;
	name: string;
	role: Role;
};

export type User = {
	id: string;
	name: string;
	role: Role;
	requests_per_minute: number;
	deleted_at: string | null;
	created_at: string;
	updated_at: string;
};
