import { CheckCircle, Loader2, Plug, RotateCcw, Save, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";

interface ServiceEntry {
	service: string;
	label: string;
	enabled: boolean;
	url: string;
	key_set: boolean;
	source: "file" | "env" | "none";
	live: boolean;
	default_port: number;
}

interface RowState {
	url: string;
	key: string;
	enabled: boolean;
	dirty: boolean;
	testing: boolean;
	saving: boolean;
	result: string;
	ok: boolean | null;
}

/**
 * Settings → Services: manage *arr credentials without touching .env.
 * Overrides persist in config/arr-services.json and take effect immediately
 * (MCP tools resolve the live client per call — no restart).
 */
export default function ServicesSection() {
	const [services, setServices] = useState<ServiceEntry[] | null>(null);
	const [rows, setRows] = useState<Record<string, RowState>>({});
	const [error, setError] = useState("");

	async function load() {
		try {
			const json = await apiFetch<{ success: boolean; data: ServiceEntry[] }>("/api/config/services");
			setServices(json.data);
			setRows((prev) => {
				const next: Record<string, RowState> = {};
				for (const s of json.data) {
					const old = prev[s.service];
					next[s.service] = {
						url: old?.dirty ? old.url : s.url,
						key: "",
						enabled: old?.dirty ? old.enabled : s.enabled,
						dirty: old?.dirty ?? false,
						testing: false,
						saving: false,
						result: old?.result ?? "",
						ok: old?.ok ?? null,
					};
				}
				return next;
			});
			setError("");
		} catch (e) {
			setError(String(e));
		}
	}

	useEffect(() => {
		load();
	}, []);

	function patch(service: string, p: Partial<RowState>) {
		setRows((prev) => ({ ...prev, [service]: { ...prev[service], ...p, dirty: true } }));
	}

	async function testRow(s: ServiceEntry) {
		const row = rows[s.service];
		if (!row || row.testing) return;
		patch(s.service, { testing: true, result: "", ok: null });
		try {
			const result = await apiFetch<{
				success: boolean;
				data: { reachable: boolean; version?: string; error?: string };
			}>("/api/config/test", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					service: s.service,
					url: row.url || `http://localhost:${s.default_port}`,
					api_key: row.key,
					use_saved: row.key === "",
				}),
				timeoutMs: 30000,
			});
			const d = result.data;
			setRows((prev) => ({
				...prev,
				[s.service]: {
					...prev[s.service],
					testing: false,
					result: d.reachable ? `Reachable (v${d.version})` : (d.error ?? "Unreachable"),
					ok: d.reachable,
				},
			}));
		} catch (e) {
			setRows((prev) => ({
				...prev,
				[s.service]: { ...prev[s.service], testing: false, result: String(e), ok: false },
			}));
		}
	}

	async function saveRow(s: ServiceEntry) {
		const row = rows[s.service];
		if (!row || row.saving) return;
		patch(s.service, { saving: true, result: "", ok: null });
		try {
			const result = await apiFetch<{
				success: boolean;
				message: string;
				data: { live: boolean; probe: { reachable: boolean; version?: string; error?: string } };
			}>("/api/config/services", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					service: s.service,
					...(row.url !== s.url ? { url: row.url } : {}),
					...(row.key !== "" ? { api_key: row.key } : {}),
					enabled: row.enabled,
				}),
				timeoutMs: 30000,
			});
			const probe = result.data.probe;
			setRows((prev) => ({
				...prev,
				[s.service]: {
					...prev[s.service],
					saving: false,
					dirty: false,
					key: "",
					result: probe.reachable
						? `Saved — live now (v${probe.version}). No restart needed.`
						: `Saved, but unreachable: ${probe.error ?? "check URL/key"}.`,
					ok: probe.reachable,
				},
			}));
			await load();
		} catch (e) {
			setRows((prev) => ({
				...prev,
				[s.service]: { ...prev[s.service], saving: false, result: String(e), ok: false },
			}));
		}
	}

	async function resetRow(s: ServiceEntry) {
		if (!window.confirm(`Remove the saved override for ${s.label} and fall back to environment variables?`)) return;
		try {
			await apiFetch(`/api/config/services/${s.service}`, { method: "DELETE" });
			await load();
		} catch (e) {
			setError(String(e));
		}
	}

	if (error) {
		return (
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4" data-testid="services-section">
				<p className="text-xs text-red-400">{error}</p>
			</section>
		);
	}

	return (
		<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4" data-testid="services-section">
			<div className="flex items-center gap-2 mb-1">
				<Plug size={18} className="text-zinc-400" />
				<h3 className="font-semibold text-sm">Services</h3>
			</div>
			<p className="text-xs text-zinc-500 mb-4">
				URLs + API keys save to <span className="font-mono">config/arr-services.json</span> and go live immediately — no{" "}
				<span className="font-mono">.env</span> editing, no restart. Keys are never shown back.
			</p>
			<div className="space-y-3">
				{(services ?? []).map((s) => {
					const row = rows[s.service];
					if (!row) return null;
					return (
						<div
							key={s.service}
							className="bg-zinc-950 border border-zinc-800 rounded-lg p-3"
							data-testid={`service-row-${s.service}`}
						>
							<div className="flex items-center justify-between mb-2">
								<div className="flex items-center gap-2">
									<span className="text-sm font-medium">{s.label}</span>
									<span
										className={`text-xs px-2 py-0.5 rounded ${
											s.live ? "bg-green-900/40 text-green-300" : "bg-zinc-800 text-zinc-500"
										}`}
									>
										{s.live ? "live" : "not configured"}
									</span>
									{s.source !== "none" && <span className="text-xs text-zinc-600 font-mono">from {s.source}</span>}
								</div>
								<label className="flex items-center gap-1.5 text-xs text-zinc-400">
									<input
										type="checkbox"
										checked={row.enabled}
										onChange={(e) => patch(s.service, { enabled: e.target.checked })}
										className="accent-zinc-300"
									/>
									enabled
								</label>
							</div>
							<div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-2">
								<input
									type="text"
									value={row.url}
									onChange={(e) => patch(s.service, { url: e.target.value })}
									placeholder={`http://localhost:${s.default_port}`}
									className="bg-zinc-800 border border-zinc-700 rounded-lg px-2.5 py-1.5 text-xs font-mono text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500"
									data-testid={`service-url-${s.service}`}
								/>
								<input
									type="password"
									value={row.key}
									onChange={(e) => patch(s.service, { key: e.target.value })}
									placeholder={s.key_set ? "key saved (leave blank to keep)" : "API key"}
									className="bg-zinc-800 border border-zinc-700 rounded-lg px-2.5 py-1.5 text-xs font-mono text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500"
									data-testid={`service-key-${s.service}`}
									autoComplete="new-password"
								/>
							</div>
							<div className="flex flex-wrap items-center gap-2">
								<button
									type="button"
									onClick={() => testRow(s)}
									disabled={row.testing}
									className="flex items-center gap-1 text-xs bg-zinc-800 hover:bg-zinc-700 px-2.5 py-1 rounded-lg disabled:opacity-50 transition-colors"
									data-testid={`service-test-${s.service}`}
								>
									{row.testing ? <Loader2 size={12} className="animate-spin" /> : null}
									Test
								</button>
								<button
									type="button"
									onClick={() => saveRow(s)}
									disabled={row.saving}
									className="flex items-center gap-1 text-xs bg-zinc-100 hover:bg-white text-zinc-900 font-medium px-2.5 py-1 rounded-lg disabled:opacity-50 transition-colors"
									data-testid={`service-save-${s.service}`}
								>
									{row.saving ? <Loader2 size={12} className="animate-spin" /> : <Save size={12} />}
									Save
								</button>
								{s.source === "file" && (
									<button
										type="button"
										onClick={() => resetRow(s)}
										className="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300 px-2 py-1 transition-colors"
										data-testid={`service-reset-${s.service}`}
									>
										<RotateCcw size={12} /> env fallback
									</button>
								)}
								{row.result && (
									<span
										className={`flex items-center gap-1 text-xs ${row.ok ? "text-green-400" : "text-yellow-400"}`}
										data-testid={`service-result-${s.service}`}
									>
										{row.ok === true ? <CheckCircle size={12} /> : row.ok === false ? <XCircle size={12} /> : null}
										{row.result}
									</span>
								)}
							</div>
						</div>
					);
				})}
				{services === null && <p className="text-xs text-zinc-600">Loading services…</p>}
			</div>
		</section>
	);
}
