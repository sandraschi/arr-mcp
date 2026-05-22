import { Activity, Bot, ChevronRight, Cpu, Play, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { API_BASE } from "../utils/api";

interface ToolDef {
	name: string;
	operations: string;
}

const tools: ToolDef[] = [
	{ name: "radarr_movies", operations: "list,lookup,get,add,delete,update,import" },
	{ name: "sonarr_series", operations: "list,lookup,get,add,delete,update" },
	{ name: "sonarr_episodes", operations: "list,get,search,set_monitored" },
	{ name: "lidarr_artists", operations: "list,lookup,get,add,delete,update" },
	{ name: "lidarr_albums", operations: "list,get,lookup,set_monitored" },
	{ name: "prowlarr_indexers", operations: "list,get,add,update,delete,test,test_all,schema" },
	{ name: "prowlarr_search", operations: "query (see params)" },
	{ name: "prowlarr_applications", operations: "list,get,sync,sync_all,test" },
	{ name: "prowlarr_history", operations: "list,since,by_indexer" },
	{ name: "readarr_authors", operations: "list,lookup,get,add,delete,update" },
	{ name: "readarr_books", operations: "list,get,lookup,set_monitored" },
	{ name: "overseerr_requests", operations: "list,get,create,approve,decline,delete,count,pending" },
	{ name: "overseerr_search", operations: "query" },
	{ name: "overseerr_users", operations: "list,get,requests" },
	{ name: "bazarr_subtitles", operations: "wanted,search,download,history,providers,languages" },
	{ name: "arr_orchestrate", operations: "request,status,check_jellyfin,queue" },
	{ name: "arr_calendar", operations: "upcoming,today,week,range" },
	{ name: "arr_stats", operations: "summary,disk,queues,history" },
	{ name: "arr_health", operations: "all,radarr,sonarr,lidarr,prowlarr,readarr,overseerr,bazarr" },
];

export default function InspectorPage() {
	const [selectedTool, setSelectedTool] = useState<ToolDef | null>(null);
	const [params, setParams] = useState<Record<string, string>>({ operation: "list" });
	const [response, setResponse] = useState("");
	const [loading, setLoading] = useState(false);
	const [raw, setRaw] = useState("");
	const resultRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (selectedTool) {
			const firstOp = selectedTool.operations.split(",")[0].split("(")[0].trim();
			setParams({ operation: firstOp });
			setResponse("");
			setRaw("");
		}
	}, [selectedTool]);

	function addParam() {
		const key = `arg${Object.keys(params).length}`;
		setParams((p) => ({ ...p, [key]: "" }));
	}

	function removeParam(key: string) {
		if (key === "operation") return;
		setParams((p) => {
			const { [key]: _, ...rest } = p;
			return rest;
		});
	}

	async function runTool() {
		if (!selectedTool) return;
		setLoading(true);
		setResponse("");
		setRaw("");

		const jsonrpc = {
			jsonrpc: "2.0",
			id: 1,
			method: "tools/call",
			params: {
				name: selectedTool.name,
				arguments: params,
			},
		};

		try {
			const res = await fetch(`${API_BASE}/mcp`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(jsonrpc),
				signal: AbortSignal.timeout(15000),
			});
			const data = await res.json();
			setRaw(JSON.stringify(data, null, 2));
			setResponse(data.result?.content?.[0]?.text || data.error?.message || JSON.stringify(data));
		} catch (e) {
			const msg = String(e);
			setResponse(msg);
			setRaw(msg);
		} finally {
			setLoading(false);
			setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
		}
	}

	function updateParam(key: string, value: string) {
		setParams((p) => ({ ...p, [key]: value }));
	}

	return (
		<div className="animate-fade-in flex flex-col h-[calc(100vh-6rem)]">
			<div className="flex items-center gap-3 mb-4">
				<Bot size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Inspector</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">{tools.length} tools</span>
			</div>

			{!selectedTool && (
				<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 overflow-y-auto flex-1">
					{tools.map((t) => (
						<button
							type="button"
							key={t.name}
							onClick={() => setSelectedTool(t)}
							className="bg-zinc-900 border border-zinc-800 rounded-xl p-3 text-left hover:border-zinc-600 transition-colors text-sm"
						>
							<code className="text-xs text-zinc-300">{t.name}</code>
							<p className="text-xs text-zinc-500 mt-1 truncate">{t.operations}</p>
						</button>
					))}
				</div>
			)}

			{selectedTool && (
				<div className="flex flex-col gap-4 flex-1 overflow-y-auto">
					<button
						type="button"
						onClick={() => setSelectedTool(null)}
						className="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300 self-start"
					>
						<ChevronRight size={12} className="rotate-180" /> Back to tools
					</button>

					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
						<h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
							<Cpu size={14} /> <code className="text-zinc-200">{selectedTool.name}</code>
						</h3>
						<p className="text-xs text-zinc-500 mb-3">Operations: {selectedTool.operations}</p>

						<div className="space-y-2">
							{Object.entries(params).map(([key, val]) => (
								<div key={key} className="flex items-center gap-2">
									<span className="text-xs text-zinc-500 w-24 font-mono shrink-0">{key}</span>
									<input
										type="text"
										value={val}
										onChange={(e) => updateParam(key, e.target.value)}
										className="flex-1 bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-xs font-mono text-zinc-300"
									/>
									{key !== "operation" && (
										<button
											type="button"
											onClick={() => removeParam(key)}
											className="text-xs text-red-500 hover:text-red-400"
										>
											x
										</button>
									)}
								</div>
							))}
						</div>

						<div className="flex items-center gap-2 mt-4">
							<button
								type="button"
								onClick={addParam}
								className="text-xs px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400"
							>
								+ Add param
							</button>
							<button
								type="button"
								onClick={runTool}
								disabled={loading}
								className="flex items-center gap-1.5 text-xs px-4 py-1.5 rounded-lg bg-zinc-700 hover:bg-zinc-600 text-zinc-200 disabled:opacity-50"
							>
								{loading ? <RefreshCw size={12} className="animate-spin" /> : <Play size={12} />}
								{loading ? "Running..." : "Run tool"}
							</button>
						</div>
					</div>

					{response && (
						<div ref={resultRef} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 animate-fade-in">
							<h4 className="text-sm font-semibold mb-2 text-zinc-300 flex items-center gap-2">
								<Activity size={14} /> Response
							</h4>
							<pre className="text-xs text-zinc-400 font-mono whitespace-pre-wrap bg-zinc-950 rounded-lg p-3 max-h-64 overflow-y-auto">
								{raw}
							</pre>
						</div>
					)}
				</div>
			)}
		</div>
	);
}
