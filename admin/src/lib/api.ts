import type { HttpError } from "@refinedev/core";

// Same-origin base path: nginx (prod) / Vite proxy (dev) forward /api to the backend, whose
// external prefix is /api/v1. The session cookie is httpOnly, so it rides along automatically.
export const API_URL = "/api/v1";

type ErrorEnvelope = {
	code?: string;
	detail?: string | unknown[];
};

async function toHttpError(response: Response): Promise<HttpError> {
	let detail: string = response.statusText;
	try {
		const body = (await response.json()) as ErrorEnvelope;
		if (typeof body.detail === "string") {
			detail = body.detail;
		} else if (Array.isArray(body.detail)) {
			detail = JSON.stringify(body.detail);
		}
	} catch {
		// Non-JSON error body; keep the status text.
	}
	return { message: detail, statusCode: response.status };
}

async function parseResponse<T>(response: Response): Promise<T> {
	if (!response.ok) {
		throw await toHttpError(response);
	}
	if (response.status === 204) {
		return undefined as T;
	}
	return (await response.json()) as T;
}

/**
 * Thin fetch wrapper: always sends the session cookie, JSON in/out, and normalises errors into
 * Refine's HttpError shape. Returns `undefined` for 204 responses.
 */
export async function apiFetch<T>(
	path: string,
	init?: RequestInit,
): Promise<T> {
	const response = await fetch(`${API_URL}${path}`, {
		credentials: "include",
		...init,
		headers: {
			"Content-Type": "application/json",
			...init?.headers,
		},
	});
	return parseResponse<T>(response);
}

/**
 * Multipart upload. The Content-Type header is intentionally left unset so the browser adds the
 * correct `multipart/form-data` boundary.
 */
export async function apiUpload<T>(
	path: string,
	formData: FormData,
): Promise<T> {
	const response = await fetch(`${API_URL}${path}`, {
		method: "POST",
		credentials: "include",
		body: formData,
	});
	return parseResponse<T>(response);
}
