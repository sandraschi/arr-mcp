/** Empty in Vite dev (proxy); absolute URL in Tauri production build. */
export const API_BASE = import.meta.env.DEV ? "" : "http://127.0.0.1:10938";
const DEFAULT_TIMEOUT = 5000;

export class ApiError extends Error {
	constructor(
		message: string,
		public status?: number,
		public data?: unknown,
	) {
		super(message);
		this.name = "ApiError";
	}
}

export async function apiFetch<T>(path: string, options?: RequestInit & { timeoutMs?: number }): Promise<T> {
	const { timeoutMs = DEFAULT_TIMEOUT, ...fetchOptions } = options ?? {};
	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), timeoutMs);
	try {
		const res = await fetch(`${API_BASE}${path}`, {
			...fetchOptions,
			signal: controller.signal,
		});
		if (!res.ok) throw new ApiError(`HTTP ${res.status}`, res.status);
		return res.json();
	} finally {
		clearTimeout(timeout);
	}
}

export interface HealthResult {
	reachable: boolean;
	version?: string;
	reason?: string;
}

export interface HealthResponse {
	success: boolean;
	data: Record<string, HealthResult>;
}

export function fetchHealth(): Promise<HealthResponse> {
	return apiFetch<HealthResponse>("/api/health");
}

export function fetchSummary(endpoint: string): Promise<{ success: boolean; data: Record<string, unknown> }> {
	return apiFetch(endpoint);
}

export function fetchLogs(
	limit = 100,
): Promise<{ success: boolean; data: { timestamp: string; level: string; message: string }[] }> {
	return apiFetch(`/api/logs?limit=${limit}`);
}
