import { AlertTriangle, CheckCircle, Inbox, Info, Search, XCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { type HealthResult, apiFetch, fetchHealth } from "../utils/api";

interface InboxItem {
	id: string;
	severity: "error" | "warn" | "info";
	source: string;
	title: string;
	detail: string;
	time: string;
}

interface LogEntry {
	timestamp: string;
	level: string;
	message: string;
}

const PAGE_SIZE = 20;

type SeverityFilter = "all" | "error" | "warn" | "info";
type SortKind = "newest" | "oldest";

function severityRank(s: InboxItem["severity"]): number {
	return s === "error" ? 0 : s === "warn" ? 1 : 2;
}

export default function InboxPage() {
	const [items, setItems] = useState<InboxItem[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [search, setSearch] = useState("");
	const [severity, setSeverity] = useState<SeverityFilter>("all");
	const [sort, setSort] = useState<SortKind>("newest");
	const [page, setPage] = useState(1);

	useEffect(() => {
		let mounted = true;
		async function load() {
			const collected: InboxItem[] = [];
			try {
				const h = await fetchHealth();
				const data: Record<string, HealthResult> = h.data ?? {};
				for (const [name, result] of Object.entries(data)) {
					if (!result.reachable) {
						collected.push({
							id: `health-${name}`,
							severity: result.reason === "not configured" ? "info" : "warn",
							source: "health",
							title: `${name}: unreachable`,
							detail: result.reason ?? "no reason reported",
							time: new Date().toISOString(),
						});
					}
				}
			} catch (e) {
				collected.push({
					id: "health-backend",
					severity: "error",
					source: "health",
					title: "Backend health check failed",
					detail: String(e),
					time: new Date().toISOString(),
				});
			}
			try {
				const logs = await apiFetch<{ success: boolean; data: LogEntry[] }>("/api/logs?limit=50");
				for (const entry of logs.data ?? []) {
					const level = (entry.level ?? "").toUpperCase();
					if (level !== "WARN" && level !== "WARNING" && level !== "ERROR") continue;
					collected.push({
						id: `log-${entry.timestamp}-${entry.message.slice(0, 24)}`,
						severity: level === "ERROR" ? "error" : "warn",
						source: "logs",
						title: entry.message.slice(0, 120),
						detail: entry.message,
						time: entry.timestamp,
					});
				}
			} catch (e) {
				if (mounted) setError(`Log feed unavailable (${String(e)}). Health alerts only.`);
			}
			if (mounted) {
				collected.sort((a, b) => severityRank(a.severity) - severityRank(b.severity) || b.time.localeCompare(a.time));
				setItems(collected);
				setLoading(false);
			}
		}
		load();
		return () => {
			mounted = false;
		};
	}, []);

	const filtered = useMemo(() => {
		const q = search.trim().toLowerCase();
		let list = items.filter((i) => {
			if (severity !== "all" && i.severity !== severity) return false;
			if (q && !`${i.title} ${i.detail} ${i.source}`.toLowerCase().includes(q)) return false;
			return true;
		});
		list = [...list].sort((a, b) => (sort === "newest" ? b.time.localeCompare(a.time) : a.time.localeCompare(b.time)));
		return list;
	}, [items, search, severity, sort]);

	const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
	const current = Math.min(page, pageCount);
	const visible = filtered.slice((current - 1) * PAGE_SIZE, current * PAGE_SIZE);

	function resetPage() {
		setPage(1);
	}

	const iconFor = (s: InboxItem["severity"]) =>
		s === "error" ? (
			<XCircle size={18} className="text-red-400 shrink-0" />
		) : s === "warn" ? (
			<AlertTriangle size={18} className="text-amber-400 shrink-0" />
		) : (
			<Info size={18} className="text-blue-400 shrink-0" />
		);

	if (loading) {
		return (
			<div className="animate-fade-in">
				<h2 className="text-2xl font-bold mb-6">Inbox</h2>
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
					<div className="h-4 bg-zinc-800 rounded w-40" />
				</div>
			</div>
		);
	}

	return (
		<div className="animate-fade-in" data-testid="inbox-page">
			<div className="flex items-center gap-3 mb-1" data-testid="inbox-header">
				<Inbox size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Inbox</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded" data-testid="inbox-count">
					{filtered.length} of {items.length}
				</span>
			</div>
			<p className="text-sm text-zinc-500 mb-4">
				Service alerts from <code className="text-zinc-400">/api/health</code> plus warnings and errors from{" "}
				<code className="text-zinc-400">/api/logs</code>.
			</p>
			{error && <p className="text-xs text-amber-400 mb-3">{error}</p>}

			<div className="flex flex-wrap items-center gap-2 mb-4">
				<div className="relative flex-1 min-w-48">
					<Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
					<input
						data-testid="inbox-search"
						value={search}
						onChange={(e) => {
							setSearch(e.target.value);
							resetPage();
						}}
						placeholder="Search alerts..."
						className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-9 pr-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
					/>
				</div>
				<select
					data-testid="inbox-filter"
					value={severity}
					onChange={(e) => {
						setSeverity(e.target.value as SeverityFilter);
						resetPage();
					}}
					className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none"
				>
					<option value="all">All severities</option>
					<option value="error">Errors</option>
					<option value="warn">Warnings</option>
					<option value="info">Info</option>
				</select>
				<select
					data-testid="inbox-sort"
					value={sort}
					onChange={(e) => {
						setSort(e.target.value as SortKind);
						resetPage();
					}}
					className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none"
				>
					<option value="newest">Newest first</option>
					<option value="oldest">Oldest first</option>
				</select>
			</div>

			{visible.length === 0 ? (
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center">
					<CheckCircle size={28} className="text-green-400 mx-auto mb-2" />
					<p className="text-sm text-zinc-300 font-medium">All clear - no alerts.</p>
					<p className="text-xs text-zinc-500 mt-1">
						{items.length === 0
							? "Every service is reachable and the log feed is quiet."
							: "Nothing matches this filter."}
					</p>
				</div>
			) : (
				<div className="space-y-2" data-testid="inbox-list">
					{visible.map((item) => (
						<div
							key={item.id}
							className="bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-3 flex items-start gap-3"
						>
							{iconFor(item.severity)}
							<div className="flex-1 min-w-0">
								<p className="text-sm text-zinc-200">{item.title}</p>
								<p className="text-xs text-zinc-500 mt-0.5 truncate">{item.detail}</p>
							</div>
							<span className="text-[11px] text-zinc-600 shrink-0">{item.source}</span>
						</div>
					))}
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
