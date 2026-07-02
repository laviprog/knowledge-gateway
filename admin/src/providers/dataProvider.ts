import type {
	BaseRecord,
	CreateParams,
	CreateResponse,
	DataProvider,
	DeleteOneParams,
	DeleteOneResponse,
	GetListParams,
	GetListResponse,
	GetOneParams,
	GetOneResponse,
	UpdateParams,
	UpdateResponse,
} from "@refinedev/core";
import { API_URL, apiFetch } from "@/lib/api";

/**
 * Data provider for the Knowledge Gateway API.
 *
 * The backend paginates with `limit`/`offset` query params and returns list responses shaped as
 * `{ total, limit, offset, <items>: [...] }`, where the array key is the plural resource name
 * (e.g. `users`, `providers`). We locate that array generically rather than hardcoding per
 * resource. The list endpoints don't support arbitrary filters/sorters, so those are ignored.
 */
function extractList<TData>(payload: Record<string, unknown>): {
	data: TData[];
	total: number;
} {
	const arrayEntry = Object.values(payload).find((value) =>
		Array.isArray(value),
	);
	const data = (arrayEntry ?? []) as TData[];
	const total = typeof payload.total === "number" ? payload.total : data.length;
	return { data, total };
}

export const dataProvider: DataProvider = {
	getApiUrl: () => API_URL,

	getList: async <TData extends BaseRecord = BaseRecord>({
		resource,
		pagination,
	}: GetListParams): Promise<GetListResponse<TData>> => {
		const pageSize = pagination?.pageSize ?? 10;
		const currentPage = pagination?.currentPage ?? 1;

		const params = new URLSearchParams();
		if (pagination?.mode !== "off") {
			params.set("limit", String(pageSize));
			params.set("offset", String((currentPage - 1) * pageSize));
		}

		const query = params.toString();
		const payload = await apiFetch<Record<string, unknown>>(
			`/${resource}${query ? `?${query}` : ""}`,
		);
		return extractList<TData>(payload);
	},

	getOne: async <TData extends BaseRecord = BaseRecord>({
		resource,
		id,
	}: GetOneParams): Promise<GetOneResponse<TData>> => {
		const data = await apiFetch<TData>(`/${resource}/${id}`);
		return { data };
	},

	create: async <TData extends BaseRecord = BaseRecord, TVariables = object>({
		resource,
		variables,
	}: CreateParams<TVariables>): Promise<CreateResponse<TData>> => {
		const data = await apiFetch<TData>(`/${resource}`, {
			method: "POST",
			body: JSON.stringify(variables),
		});
		return { data };
	},

	update: async <TData extends BaseRecord = BaseRecord, TVariables = object>({
		resource,
		id,
		variables,
	}: UpdateParams<TVariables>): Promise<UpdateResponse<TData>> => {
		const data = await apiFetch<TData>(`/${resource}/${id}`, {
			method: "PATCH",
			body: JSON.stringify(variables),
		});
		return { data };
	},

	deleteOne: async <
		TData extends BaseRecord = BaseRecord,
		TVariables = object,
	>({
		resource,
		id,
	}: DeleteOneParams<TVariables>): Promise<DeleteOneResponse<TData>> => {
		const data = await apiFetch<TData>(`/${resource}/${id}`, {
			method: "DELETE",
		});
		return { data: data ?? ({} as TData) };
	},
};
