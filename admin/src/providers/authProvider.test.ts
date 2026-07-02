import { afterEach, describe, expect, it, vi } from "vitest";
import { authProvider } from "@/providers/authProvider";

function stubFetch(body: unknown, status = 200) {
	vi.stubGlobal(
		"fetch",
		vi.fn((_input: RequestInfo | URL, _init?: RequestInit) =>
			Promise.resolve(
				new Response(status === 204 ? null : JSON.stringify(body), {
					status,
					headers: { "Content-Type": "application/json" },
				}),
			),
		),
	);
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe("authProvider", () => {
	it("login succeeds and redirects home", async () => {
		stubFetch({ id: "1", name: "admin", role: "admin" });

		const result = await authProvider.login({ name: "admin", password: "pw" });

		expect(result).toEqual({ success: true, redirectTo: "/" });
	});

	it("login fails with the backend error message", async () => {
		stubFetch({ code: "unauthorized", detail: "Invalid credentials" }, 401);

		const result = await authProvider.login({ name: "admin", password: "bad" });

		expect(result.success).toBe(false);
		expect(result.error?.message).toBe("Invalid credentials");
	});

	it("check reports authenticated on success", async () => {
		stubFetch({ id: "1", name: "admin", role: "admin" });

		expect(await authProvider.check()).toEqual({ authenticated: true });
	});

	it("check redirects to login on failure", async () => {
		stubFetch({ detail: "Unauthorized" }, 401);

		expect(await authProvider.check()).toEqual({
			authenticated: false,
			redirectTo: "/login",
		});
	});

	it("logout clears the session", async () => {
		stubFetch(null, 204);

		expect(await authProvider.logout({})).toEqual({
			success: true,
			redirectTo: "/login",
		});
	});

	it("getIdentity returns the user, or null on error", async () => {
		stubFetch({ id: "1", name: "admin", role: "admin" });
		expect(await authProvider.getIdentity?.()).toEqual({
			id: "1",
			name: "admin",
			role: "admin",
		});

		stubFetch({ detail: "Unauthorized" }, 401);
		expect(await authProvider.getIdentity?.()).toBeNull();
	});

	it("onError logs out on 401 and is a no-op otherwise", async () => {
		expect(await authProvider.onError({ statusCode: 401 })).toEqual({
			logout: true,
			redirectTo: "/login",
		});
		expect(await authProvider.onError({ statusCode: 500 })).toEqual({});
	});
});
