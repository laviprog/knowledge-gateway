import type { AuthProvider } from "@refinedev/core";
import { apiFetch } from "@/lib/api";
import type { SessionUser } from "@/types";

/**
 * Cookie-session auth against the backend `/auth` routes. The session token lives in an httpOnly
 * cookie the browser sends automatically — nothing is stored in JS/localStorage.
 */
export const authProvider: AuthProvider = {
	login: async ({ name, password }) => {
		try {
			await apiFetch<SessionUser>("/auth/login", {
				method: "POST",
				body: JSON.stringify({ name, password }),
			});
			return { success: true, redirectTo: "/" };
		} catch (error) {
			return {
				success: false,
				error: {
					name: "LoginError",
					message:
						error instanceof Error ? error.message : "Invalid credentials",
				},
			};
		}
	},

	logout: async () => {
		try {
			await apiFetch<void>("/auth/logout", { method: "POST" });
		} catch {
			// Ignore network errors on logout; the cookie is cleared server-side best-effort.
		}
		return { success: true, redirectTo: "/login" };
	},

	check: async () => {
		try {
			await apiFetch<SessionUser>("/auth/me");
			return { authenticated: true };
		} catch {
			return { authenticated: false, redirectTo: "/login" };
		}
	},

	getIdentity: async () => {
		try {
			return await apiFetch<SessionUser>("/auth/me");
		} catch {
			return null;
		}
	},

	onError: async (error) => {
		if (error?.statusCode === 401) {
			return { logout: true, redirectTo: "/login" };
		}
		return {};
	},
};
