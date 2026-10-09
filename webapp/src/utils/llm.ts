import { API_BASE, apiFetch } from "./api";

export interface OllamaModel {
	name: string;
	modified_at: string;
	size: number;
}

export interface LMStudioModel {
	id: string;
	object: string;
}

export interface LLMConfig {
	provider: "ollama" | "lmstudio" | "none";
	ollamaUrl: string;
	lmstudioUrl: string;
	selectedModel: string;
}

/**
 * Backend-proxied LLM access. The browser NEVER calls Ollama/LM Studio
 * directly: provider keys and LAN URLs stay server-side. All chat goes through
 * POST /api/chat (skill-first) or POST /api/llm/chat (raw proxy).
 */
export async function fetchBackendModels(provider: string, baseUrl?: string): Promise<string[]> {
	const params = new URLSearchParams({ provider });
	if (baseUrl) params.set("base_url", baseUrl);
	const res = await apiFetch<{ success: boolean; data: { models: string[] } }>(`/api/llm/models?${params.toString()}`);
	return res.data.models || [];
}

/** Backwards-compatible model fetchers (now backend-proxied). */
export async function fetchOllamaModels(baseUrl?: string): Promise<OllamaModel[]> {
	const names = await fetchBackendModels("ollama", baseUrl);
	return names.map((name) => ({ name, modified_at: "", size: 0 }));
}

export async function fetchLMStudioModels(baseUrl?: string): Promise<LMStudioModel[]> {
	const ids = await fetchBackendModels("lmstudio", baseUrl);
	return ids.map((id) => ({ id, object: "model" }));
}

export async function chatViaBackend(
	config: LLMConfig,
	personality: string,
	messages: { role: string; content: string }[],
): Promise<string> {
	const last = messages[messages.length - 1];
	const history = messages.slice(0, -1);
	const res = await apiFetch<{ success: boolean; data: { reply: string } }>("/api/chat", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			message: last?.content ?? "",
			history,
			personality,
			provider: config.provider,
			base_url: config.provider === "ollama" ? config.ollamaUrl : config.lmstudioUrl,
			model: config.selectedModel,
		}),
		timeoutMs: 120000,
	});
	return res.data.reply;
}

/** Raw backend proxy (no skill preprompt). Prefer chatViaBackend for Chat UI. */
export async function chatWithLLM(config: LLMConfig, messages: { role: string; content: string }[]): Promise<string> {
	if (config.provider === "none" || !config.selectedModel) {
		return "No LLM provider configured. Set up Ollama or LM Studio in Settings.";
	}
	const res = await apiFetch<{ success: boolean; data: { reply: string } }>("/api/llm/chat", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			provider: config.provider,
			base_url: config.provider === "ollama" ? config.ollamaUrl : config.lmstudioUrl,
			model: config.selectedModel,
			messages,
		}),
		timeoutMs: 120000,
	});
	return res.data.reply;
}

export async function fetchSkill(): Promise<string> {
	const res = await apiFetch<{ success: boolean; data: { skill: string } }>("/api/skills");
	return res.data.skill;
}

export async function fetchLlmProviders(): Promise<{ id: string; label: string; detected: boolean }[]> {
	const res = await apiFetch<{
		success: boolean;
		data: { providers: { id: string; label: string; detected: boolean }[] };
	}>("/api/llm/providers");
	return res.data.providers;
}

export async function fetchLogs(): Promise<string[]> {
	const res = await fetch(`${API_BASE}/api/logs?limit=1`);
	if (!res.ok) throw new Error(`HTTP ${res.status}`);
	return [];
}

const LLM_CONFIG_KEY = "arr-mcp-llm-config";

export function loadLLMConfig(): LLMConfig {
	try {
		const raw = localStorage.getItem(LLM_CONFIG_KEY);
		if (raw) return JSON.parse(raw);
	} catch {
		/* ignore */
	}
	return {
		provider: "none",
		ollamaUrl: "http://127.0.0.1:11434",
		lmstudioUrl: "http://127.0.0.1:1234",
		selectedModel: "",
	};
}

export function saveLLMConfig(config: LLMConfig): void {
	localStorage.setItem(LLM_CONFIG_KEY, JSON.stringify(config));
}
