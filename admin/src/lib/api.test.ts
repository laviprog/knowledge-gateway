import { afterEach, describe, expect, it, vi } from "vitest";
import { apiFetch, apiUpload } from "@/lib/api";

function stubFetch(response: Response) {
	const fn = vi.fn((_input: RequestInfo | URL, _init?: RequestInit) =>
		Promise.resolve(response),
	);
	vi.stubGlobal("fetch", fn);
	return fn;
}

function jsonResponse(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe("apiFetch", () => {
	it("prefixes /api/v1, sends the cookie and JSON headers, and returns parsed JSON", async () => {
		const fetchMock = stubFetch(jsonResponse({ ok: true }));

		const result = await apiFetch<{ ok: boolean }>("/users");

		expect(result).toEqual({ ok: true });
		const [url, init] = fetchMock.mock.calls[0];
		expect(url).toBe("/api/v1/users");
		expect(init?.credentials).toBe("include");
		expect((init?.headers as Record<string, string>)["Content-Type"]).toBe(
			"application/json",
		);
	});

	it("returns undefined for 204 responses", async () => {
		stubFetch(new Response(null, { status: 204 }));

		const result = await apiFetch<undefined>("/users/1", { method: "DELETE" });

		expect(result).toBeUndefined();
	});

	it("throws an HttpError with the backend detail and status code", async () => {
		stubFetch(
			jsonResponse({ code: "not_found", detail: "Resource not found" }, 404),
		);

		await expect(apiFetch("/users/1")).rejects.toMatchObject({
			message: "Resource not found",
			statusCode: 404,
		});
	});

	it("falls back to the status text when the error body is not JSON", async () => {
		stubFetch(
			new Response("boom", {
				status: 500,
				statusText: "Internal Server Error",
			}),
		);

		await expect(apiFetch("/users")).rejects.toMatchObject({ statusCode: 500 });
	});
});

describe("apiUpload", () => {
	it("posts FormData without a JSON Content-Type header", async () => {
		const fetchMock = stubFetch(jsonResponse({ id: "doc-1" }));
		const formData = new FormData();
		formData.append("file", new Blob(["hi"]), "a.txt");

		const result = await apiUpload<{ id: string }>(
			"/documents/upload",
			formData,
		);

		expect(result).toEqual({ id: "doc-1" });
		const [url, init] = fetchMock.mock.calls[0];
		expect(url).toBe("/api/v1/documents/upload");
		expect(init?.method).toBe("POST");
		expect(init?.body).toBeInstanceOf(FormData);
		expect(init?.headers).toBeUndefined();
	});
});
