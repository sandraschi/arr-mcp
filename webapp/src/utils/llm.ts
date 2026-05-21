const BACKEND = "http://127.0.0.1:10938";

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

export async function fetchOllamaModels(baseUrl: string): Promise<OllamaModel[]> {
	const res = await fetch(`${baseUrl}/api/tags`);
	if (!res.ok) throw new Error(`Ollama unavailable: ${res.status}`);
	const data = await res.json();
	return data.models || [];
}

export async function fetchLMStudioModels(baseUrl: string): Promise<LMStudioModel[]> {
	const res = await fetch(`${baseUrl}/v1/models`);
	if (!res.ok) throw new Error(`LM Studio unavailable: ${res.status}`);
	const data = await res.json();
	return data.data || [];
}

export async function chatWithLLM(config: LLMConfig, messages: { role: string; content: string }[]): Promise<string> {
	if (config.provider === "ollama") {
		const res = await fetch(`${config.ollamaUrl}/api/chat`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				model: config.selectedModel,
				messages,
				stream: false,
			}),
		});
		if (!res.ok) throw new Error(`Ollama chat failed: ${res.status}`);
		const data = await res.json();
		return data.message?.content || "";
	}

	if (config.provider === "lmstudio") {
		const res = await fetch(`${config.lmstudioUrl}/v1/chat/completions`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				model: config.selectedModel,
				messages,
			}),
		});
		if (!res.ok) throw new Error(`LM Studio chat failed: ${res.status}`);
		const data = await res.json();
		return data.choices?.[0]?.message?.content || "";
	}

	return "No LLM provider configured. Set up Ollama or LM Studio in Settings.";
}

export async function fetchLogs(): Promise<string[]> {
	const res = await fetch(`${BACKEND}/health`);
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
