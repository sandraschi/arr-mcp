/** Empty in dev (Vite proxy); direct backend URL in Tauri production build. */
export const API_BASE = import.meta.env.DEV ? "" : "http://127.0.0.1:10938";

export interface HealthResult {
	reachable: boolean;
	version?: string;
	reason?: string;
}

export interface HealthResponse {
	success: boolean;
	message: string;
	data: Record<string, HealthResult>;
}

export async function fetchHealth(): Promise<HealthResponse> {
	const res = await fetch(`${API_BASE}/api/health`);
	if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
	return res.json();
}
