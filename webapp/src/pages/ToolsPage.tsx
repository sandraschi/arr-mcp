import { ChevronDown, FlaskConical, Search, Wrench } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { mcpRequest } from "../utils/mcp";

interface ToolInfo {
	name: string;
	description: string;
	schema?: {
		properties?: Record<string, { type?: string; description?: string; enum?: string[] }>;
		required?: string[];
	};
	isPortmanteau: boolean;
	live: boolean;
}

// Static fallback when the MCP endpoint is unreachable (mirrors InspectorPage).
const FALLBACK_OPS: Array<{ name: string; operations: string }> = [
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

const PAGE_SIZE = 20;

type FilterKind = "all" | "portmanteau" | "solo";
type SortKind = "name-asc" | "name-desc";

export default function ToolsPage() {
	const [tools, setTools] = useState<ToolInfo[]>([]);
	const [loading, setLoading] = useState(true);
	const [live, setLive] = useState(false);
	const [error, setError] = useState("");
	const [search, setSearch] = useState("");
	const [filter, setFilter] = useState<FilterKind>("all");
	const [sort, setSort] = useState<SortKind>("name-asc");
	const [page, setPage] = useState(1);
	const [expanded, setExpanded] = useState<string | null>(null);

	useEffect(() => {
		let mounted = true;
		async function load() {
			try {
				const result = await mcpRequest("tools/list", {});
				const listed: Array<{ name: string; description?: string; inputSchema?: ToolInfo["schema"] }> =
					result?.tools ?? [];
				if (mounted) {
					setTools(
						listed.map((t) => ({
							name: t.name,
							description: t.description ?? "",
							schema: t.inputSchema,
							isPortmanteau: t.inputSchema?.properties?.operation != null,
							live: true,
						})),
					);
					setLive(true);
				}
			} catch (e) {
				if (mounted) {
					setError(`Live discovery failed (${String(e)}). Showing static registry.`);
					setTools(
						FALLBACK_OPS.map((t) => ({
							name: t.name,
							description: `Operations: ${t.operations}`,
							isPortmanteau: true,
							live: false,
						})),
					);
				}
			} finally {
				if (mounted) setLoading(false);
			}
		}
		load();
		return () => {
			mounted = false;
		};
	}, []);

	const filtered = useMemo(() => {
		const q = search.trim().toLowerCase();
		let list = tools.filter((t) => {
			if (filter === "portmanteau" && !t.isPortmanteau) return false;
			if (filter === "solo" && t.isPortmanteau) return false;
			if (q && !`${t.name} ${t.description}`.toLowerCase().includes(q)) return false;
			return true;
		});
		list = [...list].sort((a, b) =>
			sort === "name-asc" ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name),
		);
		return list;
	}, [tools, search, filter, sort]);

	const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
	const current = Math.min(page, pageCount);
	const visible = filtered.slice((current - 1) * PAGE_SIZE, current * PAGE_SIZE);

	function resetPage() {
		setPage(1);
	}

	if (loading) {
		return (
			<div className="animate-fade-in">
				<h2 className="text-2xl font-bold mb-6">Tools</h2>
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
					<div className="h-4 bg-zinc-800 rounded w-40" />
				</div>
			</div>
		);
	}

	return (
		<div className="animate-fade-in" data-testid="tools-page">
			<div className="flex items-center gap-3 mb-1" data-testid="tools-header">
				<Wrench size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Tools</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded" data-testid="tools-count">
					{filtered.length} of {tools.length}
				</span>
				<span
					className={`text-xs px-2 py-0.5 rounded ${live ? "bg-green-900/40 text-green-300" : "bg-amber-900/40 text-amber-300"}`}
				>
					{live ? "live (MCP discovery)" : "static fallback"}
				</span>
			</div>
			<p className="text-sm text-zinc-500 mb-4">
				Discovered from the server via <code className="text-zinc-400">tools/list</code>. Portmanteaus expand to show
				parameters and schema.{" "}
				<Link to="/inspector" className="text-blue-400 hover:underline">
					Try them in the Inspector
				</Link>
				.
			</p>
			{error && <p className="text-xs text-amber-400 mb-3">{error}</p>}

			<div className="flex flex-wrap items-center gap-2 mb-4">
				<div className="relative flex-1 min-w-48">
					<Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
					<input
						data-testid="tools-search"
						value={search}
						onChange={(e) => {
							setSearch(e.target.value);
							resetPage();
						}}
						placeholder="Search tools..."
						className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-9 pr-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
					/>
				</div>
				<select
					data-testid="tools-filter"
					value={filter}
					onChange={(e) => {
						setFilter(e.target.value as FilterKind);
						resetPage();
					}}
					className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none"
				>
					<option value="all">All kinds</option>
					<option value="portmanteau">Portmanteau</option>
					<option value="solo">Solo</option>
				</select>
				<select
					data-testid="tools-sort"
					value={sort}
					onChange={(e) => {
						setSort(e.target.value as SortKind);
						resetPage();
					}}
					className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none"
				>
					<option value="name-asc">Name A-Z</option>
					<option value="name-desc">Name Z-A</option>
				</select>
			</div>

			{visible.length === 0 ? (
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center text-sm text-zinc-500">
					No tools match this filter.
				</div>
			) : (
				<div className="space-y-2" data-testid="tools-list">
					{visible.map((t) => {
						const isOpen = expanded === t.name;
						const props = t.schema?.properties ?? {};
						return (
							<div key={t.name} className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
								<button
									type="button"
									onClick={() => setExpanded(isOpen ? null : t.name)}
									className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-zinc-800/40 transition-colors"
								>
									<code className="text-sm text-zinc-200">{t.name}</code>
									<span
										className={`text-[11px] px-1.5 py-0.5 rounded ${t.isPortmanteau ? "bg-blue-900/40 text-blue-300" : "bg-zinc-800 text-zinc-400"}`}
									>
										{t.isPortmanteau ? "portmanteau" : "solo"}
									</span>
									<span className="flex-1" />
									<ChevronDown
										size={16}
										className={`text-zinc-500 transition-transform ${isOpen ? "rotate-180" : ""}`}
									/>
								</button>
								{isOpen && (
									<div className="px-4 pb-4 border-t border-zinc-800 pt-3">
										{t.description && <p className="text-sm text-zinc-400 mb-3">{t.description}</p>}
										{Object.keys(props).length > 0 ? (
											<table className="w-full text-xs">
												<thead>
													<tr className="text-left text-zinc-500 border-b border-zinc-800">
														<th className="pb-1 pr-2 font-medium">Parameter</th>
														<th className="pb-1 pr-2 font-medium">Type</th>
														<th className="pb-1 font-medium">Description</th>
													</tr>
												</thead>
												<tbody>
													{Object.entries(props).map(([pname, pdef]) => (
														<tr key={pname} className="border-b border-zinc-800/50">
															<td className="py-1.5 pr-2">
																<code className="text-zinc-200">{pname}</code>
																{t.schema?.required?.includes(pname) && <span className="text-red-400 ml-1">*</span>}
															</td>
															<td className="py-1.5 pr-2 text-zinc-500">{pdef.type ?? "-"}</td>
															<td className="py-1.5 text-zinc-400">
																{pdef.description ?? "-"}
																{pdef.enum && <span className="text-zinc-500"> ({pdef.enum.join(", ")})</span>}
															</td>
														</tr>
													))}
												</tbody>
											</table>
										) : (
											<p className="text-xs text-zinc-600 flex items-center gap-1.5">
												<FlaskConical size={14} /> No parameter schema exposed - see the Inspector for usage.
											</p>
										)}
									</div>
								)}
							</div>
						);
					})}
				</div>
			)}

			{pageCount > 1 && (
				<div className="flex items-center gap-2 mt-4 text-sm">
					<button
						type="button"
						disabled={current <= 1}
						onClick={() => setPage((p) => Math.max(1, p - 1))}
						className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-300 disabled:opacity-40"
					>
						Prev
					</button>
					<span className="text-xs text-zinc-500">
						Page {current} of {pageCount}
					</span>
					<button
						type="button"
						disabled={current >= pageCount}
						onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
						className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-300 disabled:opacity-40"
					>
						Next
					</button>
				</div>
			)}
		</div>
	);
}
