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
	const res = await fetch("/health");
	if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
	return res.json();
}
