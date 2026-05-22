import { Activity, Download, Filter, Pause, Play, Trash2 } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { API_BASE, fetchLogs } from "../utils/api";

export default function LoggerPage() {
	const [lines, setLines] = useState<{ timestamp: string; level: string; message: string }[]>([]);
	const [paused, setPaused] = useState(false);
	const [connected, setConnected] = useState(false);
	const [sse, setSse] = useState(false);
	const [error, setError] = useState("");
	const [filter, setFilter] = useState("");
	const pausedRef = useRef(false);
	const bottomRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		pausedRef.current = paused;
	}, [paused]);

	useEffect(() => {
		let mounted = true;
		let interval: ReturnType<typeof setInterval> | null = null;

		const es = new EventSource(`${API_BASE}/api/logs/stream`);
		es.onopen = () => {
			if (mounted) setSse(true);
		};
		es.onmessage = (ev) => {
			if (!mounted || pausedRef.current) return;
			try {
				const entry = JSON.parse(ev.data);
				if (entry?.message) {
					setLines((prev) =>
						[{ timestamp: entry.timestamp || "", level: entry.level || "INFO", message: entry.message }, ...prev].slice(
							0,
							500,
						),
					);
					if (mounted) {
						setConnected(true);
						setError("");
					}
				}
			} catch {
				/* skip malformed */
			}
		};
		es.onerror = () => {
			es.close();
			if (!mounted) return;
			setSse(false);
			interval = setInterval(async () => {
				try {
					const json = await fetchLogs(200);
					if (!mounted) return;
					if (json.data) {
						setLines((prev) => {
							const existing = new Set(prev.map((e) => `${e.timestamp}|${e.level}|${e.message}`));
							const fresh = json.data.filter((e) => !existing.has(`${e.timestamp}|${e.level}|${e.message}`));
							return fresh.length > 0 ? [...fresh, ...prev].slice(0, 500) : prev;
						});
						setConnected(true);
						setError("");
					}
				} catch (e) {
					if (mounted) {
						setConnected(false);
						setError(String(e));
					}
				}
			}, 2000);
		};

		return () => {
			mounted = false;
			es.close();
			if (interval) clearInterval(interval);
		};
	}, []);

	useEffect(() => {
		if (!paused) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [lines, paused]);

	const display = useMemo(() => {
		if (!filter.trim()) return lines;
		return lines.filter(
			(l) =>
				l.message.toLowerCase().includes(filter.toLowerCase()) || l.level.toLowerCase().includes(filter.toLowerCase()),
		);
	}, [lines, filter]);

	return (
		<div className="space-y-4 max-w-6xl mx-auto">
			<div className="flex items-center justify-between">
				<h2 className="text-2xl font-bold text-white flex items-center gap-3">
					<Activity className="text-emerald-500" /> Server Logs
				</h2>
				<div className="flex flex-wrap items-center gap-2">
					<div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 flex-1 min-w-[160px] max-w-xs">
						<Filter size={14} className="text-zinc-500 shrink-0" />
						<input
							type="text"
							placeholder="Filter..."
							value={filter}
							onChange={(e) => setFilter(e.target.value)}
							className="bg-transparent text-sm text-zinc-300 placeholder-zinc-600 outline-none w-full"
						/>
					</div>
					<span
						className={`text-xs font-mono px-2.5 py-1.5 rounded-lg border ${
							connected ? "border-emerald-500/30 text-emerald-400" : "border-red-500/30 text-red-400"
						}`}
					>
						{sse ? "SSE" : `${lines.length} entries`} {!connected && (error || "disconnected")}
					</span>
					<button
						type="button"
						onClick={() => setPaused((p) => !p)}
						className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-zinc-800 text-sm text-zinc-300 hover:bg-zinc-800"
					>
						{paused ? <Play size={12} /> : <Pause size={12} />} {paused ? "Tail" : "Pause"}
					</button>
					<button
						type="button"
						onClick={() => {
							const text = lines.map((l) => `[${l.timestamp}] ${l.level}: ${l.message}`).join("\n");
							const b = new Blob([text], { type: "text/plain" });
							const a = document.createElement("a");
							a.href = URL.createObjectURL(b);
							a.download = `arr-mcp-${new Date().toISOString().slice(0, 10)}.log`;
							a.click();
						}}
						className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-emerald-500/20 text-sm text-emerald-300 hover:bg-emerald-500/10"
					>
						<Download size={12} /> Export
					</button>
					<button
						type="button"
						onClick={() => setLines([])}
						className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-red-500/20 text-sm text-red-300 hover:bg-red-500/10"
					>
						<Trash2 size={12} /> Clear
					</button>
				</div>
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
				<div className="px-4 py-2 border-b border-zinc-800 flex items-center justify-between text-sm text-zinc-400">
					<span className="flex items-center gap-2">
						<Activity size={10} className="text-emerald-500" /> {sse ? "/api/logs/stream (SSE)" : "/api/logs (poll 2s)"}
					</span>
					<span>{display.length} lines</span>
				</div>
				<div className="h-[60vh] overflow-y-auto p-4 font-mono text-xs text-zinc-300 whitespace-pre-wrap break-all">
					{display.length === 0 ? (
						<span className="text-zinc-500 italic">No log lines.</span>
					) : (
						display.map((entry, i) => (
							<div key={`${entry.timestamp}-${i}`} className="hover:bg-zinc-800/30 py-px">
								<span className="text-zinc-600">{entry.timestamp}</span>{" "}
								<span
									className={`font-semibold ${entry.level === "ERROR" ? "text-red-400" : entry.level === "WARNING" ? "text-yellow-400" : "text-zinc-400"}`}
								>
									{entry.level}:
								</span>{" "}
								{entry.message}
							</div>
						))
					)}
					<div ref={bottomRef} />
				</div>
			</div>
		</div>
	);
}
