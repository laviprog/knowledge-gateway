import { afterEach, describe, expect, it, vi } from "vitest";
import { dataProvider } from "@/providers/dataProvider";

function stubFetch(body: unknown, status = 200) {
	const fn = vi.fn((_input: RequestInfo | URL, _init?: RequestInit) =>
		Promise.resolve(
			new Response(status === 204 ? null : JSON.stringify(body), {
				status,
				headers: { "Content-Type": "application/json" },
			}),
		),
	);
	vi.stubGlobal("fetch", fn);
	return fn;
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe("dataProvider", () => {
	it("exposes the API url", () => {
		expect(dataProvider.getApiUrl()).toBe("/api/v1");
	});

	it("getList maps pagination to limit/offset and extracts the array + total", async () => {
		const fetchMock = stubFetch({
			users: [{ id: "1" }, { id: "2" }],
			total: 42,
		});

		const result = await dataProvider.getList({
			resource: "users",
			pagination: { currentPage: 3, pageSize: 10 },
		});

		expect(result).toEqual({ data: [{ id: "1" }, { id: "2" }], total: 42 });
		const url = fetchMock.mock.calls[0][0] as string;
		expect(url).toContain("/api/v1/users?");
		expect(url).toContain("limit=10");
		expect(url).toContain("offset=20");
	});

	it("getList omits pagination params when mode is off", async () => {
		const fetchMock = stubFetch({ providers: [], total: 0 });

		await dataProvider.getList({
			resource: "providers",
			pagination: { mode: "off" },
		});

		expect(fetchMock.mock.calls[0][0]).toBe("/api/v1/providers");
	});

	it("getList falls back to array length when total is missing", async () => {
		stubFetch({ items: [{ id: "1" }] });

		const result = await dataProvider.getList({ resource: "documents" });

		expect(result.total).toBe(1);
	});

	it("getOne fetches by id", async () => {
		const fetchMock = stubFetch({ id: "7", name: "acme" });

		const result = await dataProvider.getOne({ resource: "users", id: "7" });

		expect(result.data).toEqual({ id: "7", name: "acme" });
		expect(fetchMock.mock.calls[0][0]).toBe("/api/v1/users/7");
	});

	it("create posts the variables", async () => {
		const fetchMock = stubFetch({ id: "new" });

		const result = await dataProvider.create({
			resource: "users",
			variables: { name: "a" },
		});

		expect(result.data).toEqual({ id: "new" });
		const init = fetchMock.mock.calls[0][1];
		expect(init?.method).toBe("POST");
		expect(init?.body).toBe(JSON.stringify({ name: "a" }));
	});

	it("update patches by id", async () => {
		const fetchMock = stubFetch({ id: "7", name: "b" });

		await dataProvider.update({
			resource: "users",
			id: "7",
			variables: { name: "b" },
		});

		const [url, init] = fetchMock.mock.calls[0];
		expect(url).toBe("/api/v1/users/7");
		expect(init?.method).toBe("PATCH");
	});

	it("deleteOne handles a 204 response", async () => {
		const fetchMock = stubFetch(null, 204);

		const result = await dataProvider.deleteOne({ resource: "users", id: "7" });

		expect(result.data).toEqual({});
		expect(fetchMock.mock.calls[0][1]?.method).toBe("DELETE");
	});
});
