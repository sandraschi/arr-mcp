import { create } from "zustand";

const BASE = import.meta.env.DEV ? "" : "http://127.0.0.1:10938";

interface ConnectionState {
	status: "connecting" | "connected" | "offline";
	error: string | null;
	check: () => Promise<void>;
	setStatus: (s: ConnectionState["status"]) => void;
}

export const useConnection = create<ConnectionState>((set) => ({
	status: "connecting",
	error: null,
	check: async () => {
		try {
			const res = await fetch(`${BASE}/api/health`, { signal: AbortSignal.timeout(5000) });
			if (res.ok) set({ status: "connected", error: null });
			else set({ status: "offline", error: `HTTP ${res.status}` });
		} catch {
			set({ status: "offline", error: null });
		}
	},
	setStatus: (status) => set({ status }),
}));
