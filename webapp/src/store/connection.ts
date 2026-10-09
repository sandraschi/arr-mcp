import { create } from "zustand";

/** Absolute backend URL only inside the Tauri webview; same-origin otherwise. */
function isTauri(): boolean {
	return typeof window !== "undefined" && ("__TAURI__" in window || "__TAURI_INTERNALS__" in window);
}

const BASE = isTauri() ? "http://127.0.0.1:10938" : "";

interface ConnectionState {
	status: "connecting" | "connected" | "offline";
	error: string | null;
	check: () => Promise<void>;
	setStatus: (s: ConnectionState["status"]) => void;
}

let tauriListening = false;

async function ensureTauriListener(set: (s: Partial<ConnectionState>) => void) {
	// Tauri webview: prefer the backend-status event when available,
	// fall back to HTTP polling (dev browser has no Tauri runtime).
	if (tauriListening) return;
	tauriListening = true;
	try {
		const mod = await import("@tauri-apps/api/event").catch(() => null);
		if (mod) {
			await mod.listen<string>("backend-status", (event) => {
				if (event.payload === "ready") set({ status: "connected", error: null });
			});
		}
	} catch {
		/* no Tauri runtime - HTTP poll below covers it */
	}
}

export const useConnection = create<ConnectionState>((set) => ({
	status: "connecting",
	error: null,
	check: async () => {
		try {
			await ensureTauriListener(set);
			const res = await fetch(`${BASE}/api/health`, { signal: AbortSignal.timeout(5000) });
			if (res.ok) set({ status: "connected", error: null });
			else set({ status: "offline", error: `HTTP ${res.status}` });
		} catch {
			set({ status: "offline", error: null });
		}
	},
	setStatus: (status) => set({ status }),
}));
