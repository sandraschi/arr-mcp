import { CheckCircle, Cpu, Key, RefreshCw, Save, Server, Settings, Wifi, XCircle } from "lucide-react";
import { useState } from "react";
import { type HealthResult, fetchHealth } from "../utils/api";
import { type LLMConfig, fetchLMStudioModels, fetchOllamaModels, loadLLMConfig, saveLLMConfig } from "../utils/llm";

export default function SettingsPage() {
	const [llmConfig, setLLMConfig] = useState<LLMConfig>(loadLLMConfig);
	const [health, setHealth] = useState<HealthResult | null>(null);
	const [saved, setSaved] = useState(false);

	const arrPorts: Record<string, number> = {
		radarr: 7878,
		sonarr: 8989,
		lidarr: 8686,
		prowlarr: 9696,
		readarr: 8787,
		overseerr: 5055,
		bazarr: 6767,
		jellyfin: 8096,
	};

	async function checkHealth() {
		try {
			const h = await fetchHealth();
			const firstKey = Object.keys(h.data)[0];
			setHealth(h.data[firstKey] || null);
		} catch {
			setHealth({ reachable: false, reason: "Backend unreachable" });
		}
	}

	function handleSaveLLM() {
		saveLLMConfig(llmConfig);
		setSaved(true);
		setTimeout(() => setSaved(false), 2000);
	}

	return (
		<div className="animate-fade-in max-w-2xl">
			<div className="flex items-center gap-3 mb-6">
				<Settings size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Settings</h2>
			</div>

			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-4">
					<Server size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Backend Connection</h3>
				</div>
				<div className="flex items-center gap-3 mb-3">
					<span className="text-xs text-zinc-500">arr-mcp backend (port 10938)</span>
					<button
						type="button"
						onClick={checkHealth}
						className="flex items-center gap-1.5 text-xs bg-zinc-800 hover:bg-zinc-700 px-2.5 py-1 rounded-lg transition-colors"
					>
						<RefreshCw size={12} />
						Check
					</button>
				</div>
				{health && (
					<div
						className={`flex items-center gap-2 text-sm p-3 rounded-lg ${
							health.reachable ? "bg-green-900/20 text-green-400" : "bg-red-900/20 text-red-400"
						}`}
					>
						{health.reachable ? <CheckCircle size={16} /> : <XCircle size={16} />}
						<span>{health.reachable ? `Connected — v${health.version || "?"}` : health.reason || "Unreachable"}</span>
					</div>
				)}
			</section>

			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-4">
					<Cpu size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Local LLM</h3>
				</div>

				<div className="space-y-3">
					<div>
						<label className="text-xs text-zinc-500 block mb-1">Provider</label>
						<select
							value={llmConfig.provider}
							onChange={(e) => setLLMConfig({ ...llmConfig, provider: e.target.value as LLMConfig["provider"] })}
							className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm"
						>
							<option value="none">None</option>
							<option value="ollama">Ollama</option>
							<option value="lmstudio">LM Studio</option>
						</select>
					</div>

					{llmConfig.provider === "ollama" && (
						<div>
							<label className="text-xs text-zinc-500 block mb-1">Ollama API URL</label>
							<input
								type="text"
								value={llmConfig.ollamaUrl}
								onChange={(e) => setLLMConfig({ ...llmConfig, ollamaUrl: e.target.value })}
								className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm font-mono"
								placeholder="http://127.0.0.1:11434"
							/>
						</div>
					)}

					{llmConfig.provider === "lmstudio" && (
						<div>
							<label className="text-xs text-zinc-500 block mb-1">LM Studio API URL</label>
							<input
								type="text"
								value={llmConfig.lmstudioUrl}
								onChange={(e) => setLLMConfig({ ...llmConfig, lmstudioUrl: e.target.value })}
								className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm font-mono"
								placeholder="http://127.0.0.1:1234"
							/>
						</div>
					)}
				</div>

				<button
					type="button"
					onClick={handleSaveLLM}
					className="mt-4 flex items-center gap-2 bg-zinc-700 hover:bg-zinc-600 px-4 py-2 rounded-lg text-sm transition-colors"
				>
					{saved ? <CheckCircle size={14} className="text-green-400" /> : <Save size={14} />}
					{saved ? "Saved" : "Save LLM Config"}
				</button>
			</section>

			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-4">
					<Wifi size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">*Arr Service Ports</h3>
					<span className="text-xs text-zinc-600">(reference only)</span>
				</div>
				<div className="grid grid-cols-2 gap-2 text-sm">
					{Object.entries(arrPorts).map(([name, port]) => (
						<div key={name} className="flex items-center justify-between bg-zinc-800 rounded-lg px-3 py-1.5">
							<span className="capitalize text-zinc-400">{name}</span>
							<code className="text-xs text-zinc-300 font-mono">:{port}</code>
						</div>
					))}
				</div>
			</section>

			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<div className="flex items-center gap-2 mb-4">
					<Key size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">API Keys</h3>
				</div>
				<p className="text-xs text-zinc-500 mb-2">Configure API keys via environment variables or the .env file:</p>
				<div className="bg-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-400 overflow-x-auto">
					<pre>{`RADARR_API_KEY=your-key
SONARR_API_KEY=your-key
LIDARR_API_KEY=your-key
PROWLARR_API_KEY=your-key
READARR_API_KEY=your-key
OVERSEERR_API_KEY=your-key
BAZARR_API_KEY=your-key
JELLYFIN_API_KEY=your-key`}</pre>
				</div>
			</section>
		</div>
	);
}
