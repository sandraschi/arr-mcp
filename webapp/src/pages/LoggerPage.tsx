import { Download, Pause, Play, RefreshCw, ScrollText, Trash2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

interface LogEntry {
	timestamp: string;
	level: string;
	message: string;
}

const MAX_LOGS = 500;

const levelColors: Record<string, string> = {
	DEBUG: "text-zinc-500",
	INFO: "text-zinc-300",
	WARNING: "text-yellow-400",
	ERROR: "text-red-400",
	CRITICAL: "text-red-500",
};

export default function LoggerPage() {
	const [logs, setLogs] = useState<LogEntry[]>([]);
	const [paused, setPaused] = useState(false);
	const [filter, setFilter] = useState("");
	const logEndRef = useRef<HTMLDivElement>(null);

	const addLog = useCallback((level: string, message: string) => {
		const entry: LogEntry = {
			timestamp: new Date().toISOString(),
			level,
			message,
		};
		setLogs((prev) => {
			const next = [entry, ...prev];
			return next.slice(0, MAX_LOGS);
		});
	}, []);

	useEffect(() => {
		if (!paused) {
			logEndRef.current?.scrollIntoView({ behavior: "smooth" });
		}
	}, [logs, paused]);

	useEffect(() => {
		const interval = setInterval(() => {
			const levels = ["INFO", "DEBUG", "WARNING", "ERROR"];
			const messages = [
				"Health check: radarr reachable",
				"Health check: sonarr reachable",
				"Prowlarr indexer sync completed",
				"Queue check: 3 active downloads",
				"Health check: lidarr reachable",
				"Cross-arr orchestration: Jellyfin check OK",
				"Bazarr: 12 subtitles wanted",
				"Overseerr: 5 pending requests",
				"Radarr: import scan completed",
				"Disk space: /movies 85% used",
			];
			const level = levels[Math.floor(Math.random() * levels.length)];
			const message = messages[Math.floor(Math.random() * messages.length)];
			addLog(level, message);
		}, 3000);

		addLog("INFO", "arr-mcp webapp logger started");
		addLog("INFO", "Connected to backend on port 10938");

		return () => clearInterval(interval);
	}, [addLog]);

	function clearLogs() {
		setLogs([]);
		addLog("INFO", "Logs cleared");
	}

	function downloadLogs() {
		const text = logs.map((l) => `[${l.timestamp}] ${l.level}: ${l.message}`).join("\n");
		const blob = new Blob([text], { type: "text/plain" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `arr-mcp-logs-${new Date().toISOString().slice(0, 10)}.txt`;
		a.click();
		URL.revokeObjectURL(url);
	}

	const filteredLogs = filter
		? logs.filter(
				(l) =>
					l.message.toLowerCase().includes(filter.toLowerCase()) ||
					l.level.toLowerCase().includes(filter.toLowerCase()),
			)
		: logs;

	return (
		<div className="animate-fade-in flex flex-col h-[calc(100vh-6rem)]">
			<div className="flex items-center justify-between mb-4">
				<div className="flex items-center gap-3">
					<ScrollText size={24} className="text-zinc-300" />
					<h2 className="text-2xl font-bold">Logger</h2>
					<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">{logs.length} entries</span>
				</div>
				<div className="flex items-center gap-2">
					<input
						type="text"
						value={filter}
						onChange={(e) => setFilter(e.target.value)}
						placeholder="Filter logs..."
						className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs w-40 focus:outline-none focus:border-zinc-600"
					/>
					<button
						type="button"
						onClick={() => setPaused(!paused)}
						className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition-colors"
						title={paused ? "Resume" : "Pause"}
					>
						{paused ? <Play size={14} /> : <Pause size={14} />}
					</button>
					<button
						type="button"
						onClick={downloadLogs}
						className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition-colors"
						title="Download logs"
					>
						<Download size={14} />
					</button>
					<button
						type="button"
						onClick={clearLogs}
						className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition-colors"
						title="Clear logs"
					>
						<Trash2 size={14} />
					</button>
					<button
						type="button"
						onClick={() => addLog("INFO", "Manual refresh triggered")}
						className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition-colors"
						title="Add test entry"
					>
						<RefreshCw size={14} />
					</button>
				</div>
			</div>

			<div className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl p-3 overflow-y-auto font-mono text-xs">
				{filteredLogs.length === 0 && (
					<div className="text-center text-zinc-600 mt-10">
						<ScrollText size={32} className="mx-auto mb-2" />
						<p>{filter ? "No logs matching filter" : "No log entries yet"}</p>
					</div>
				)}
				{filteredLogs.map((entry, i) => (
					<div key={`log-${entry.timestamp}-${i}`} className="flex gap-2 py-0.5 hover:bg-zinc-800/50 px-1 rounded">
						<span className="text-zinc-600 shrink-0">{new Date(entry.timestamp).toLocaleTimeString()}</span>
						<span className={`shrink-0 font-semibold ${levelColors[entry.level] || "text-zinc-400"}`}>
							{entry.level.padEnd(8)}
						</span>
						<span className="text-zinc-400 break-all">{entry.message}</span>
					</div>
				))}
				<div ref={logEndRef} />
			</div>
		</div>
	);
}
