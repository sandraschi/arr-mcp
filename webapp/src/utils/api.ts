const BASE = "";

export interface HealthResult {
	reachable: boolean;
	version?: string;
	reason?: string;
}

export interface StackHealth {
	success: boolean;
	message: string;
	data: Record<string, HealthResult>;
}

export interface StackStats {
	success: boolean;
	message: string;
	data: Record<string, Record<string, unknown>>;
}

export async function fetchHealth(): Promise<StackHealth> {
	const res = await fetch(`${BASE}/health`);
	if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
	return res.json();
}

export async function fetchStats(operation: string): Promise<StackStats> {
	const res = await fetch(`${BASE}/api/stats?operation=${operation}`);
	if (!res.ok) throw new Error(`Stats failed: ${res.status}`);
	return res.json();
}

export async function fetchCalendar(operation: string): Promise<StackStats> {
	const res = await fetch(`${BASE}/api/calendar?operation=${operation}`);
	if (!res.ok) throw new Error(`Calendar failed: ${res.status}`);
	return res.json();
}
