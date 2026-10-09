import { create } from "zustand";
import { API_BASE } from "../utils/api";

interface LlmState {
	ollamaDetected: boolean | null;
	lmstudioDetected: boolean | null;
	probing: boolean;
	refresh: () => Promise<void>;
}

/**
 * Global LLM provider state (fleet WEBAPP_SOTA_STANDARDS §VI).
 * Detection runs server-side (GET /api/llm/discover) so the browser never
 * probes provider ports directly. null = not probed yet.
 */
export const useLlm = create<LlmState>((set) => ({
	ollamaDetected: null,
	lmstudioDetected: null,
	probing: false,
	refresh: async () => {
		set({ probing: true });
		try {
			const res = await fetch(`${API_BASE}/api/llm/discover`, { signal: AbortSignal.timeout(8000) });
			if (res.ok) {
				const json = (await res.json()) as {
					data: { ollama: boolean; lmstudio: boolean };
				};
				set({ ollamaDetected: json.data.ollama, lmstudioDetected: json.data.lmstudio });
			} else {
				set({ ollamaDetected: false, lmstudioDetected: false });
			}
		} catch {
			set({ ollamaDetected: false, lmstudioDetected: false });
		} finally {
			set({ probing: false });
		}
	},
}));
