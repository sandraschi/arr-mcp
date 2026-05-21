import { AlertTriangle, HardDrive, Package, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import type { ReactNode } from "react";

interface SummaryData {
	movies?: number;
	series?: number;
	artists?: number;
	authors?: number;
	wanted?: number;
	queue?: number;
	disk?: { path: string; freeSpace: number; totalSpace: number }[];
	indexers?: number;
	applications?: number;
	stats?: Record<string, unknown>;
	enabled?: boolean;
	error?: string;
	movies_wanted?: number;
	episodes_wanted?: number;
	providers?: number;
	total_requests?: number;
	pending?: number;
	total_wanted?: number;
}

export default function RadarrPage() {
	return <ServicePage title="Radarr" subtitle="Movies" color="radarr" endpoint="/api/radarr/summary" />;
}

export function SonarrPageWrapped() {
	return <ServicePage title="Sonarr" subtitle="TV Series" color="sonarr" endpoint="/api/sonarr/summary" />;
}

export function LidarrPageWrapped() {
	return <ServicePage title="Lidarr" subtitle="Music" color="lidarr" endpoint="/api/lidarr/summary" />;
}

export function ProwlarrPageWrapped() {
	return <ServicePage title="Prowlarr" subtitle="Indexer Backbone" color="prowlarr" endpoint="/api/prowlarr/summary" />;
}

export function ReadarrPageWrapped() {
	return <ServicePage title="Readarr" subtitle="Books" color="readarr" endpoint="/api/readarr/summary" />;
}

export function OverseerrPageWrapped() {
	return (
		<ServicePage
			title="Overseerr"
			subtitle="Requests & Discovery"
			color="overseerr"
			endpoint="/api/overseerr/summary"
		/>
	);
}

export function BazarrPageWrapped() {
	return <ServicePage title="Bazarr" subtitle="Subtitles" color="bazarr" endpoint="/api/bazarr/summary" />;
}

export function ServicePage({
	title,
	subtitle,
	color,
	endpoint,
}: {
	title: string;
	subtitle: string;
	color: string;
	endpoint: string;
}) {
	const [data, setData] = useState<SummaryData | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [raw, setRaw] = useState<Record<string, unknown> | null>(null);

	useEffect(() => {
		let mounted = true;
		async function poll() {
			try {
				const res = await fetch(endpoint);
				if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
				const json = await res.json();
				if (mounted) {
					setData(json.data);
					setRaw(json.data);
					setError("");
				}
			} catch (e) {
				if (mounted) setError(String(e));
			} finally {
				if (mounted) setLoading(false);
			}
		}
		poll();
		const interval = setInterval(poll, 30000);
		return () => {
			mounted = false;
			clearInterval(interval);
		};
	}, [endpoint]);

	if (loading) {
		return (
			<div className="animate-fade-in">
				<PageHeader title={title} subtitle={subtitle} color={color} />
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
					<Skeleton />
					<Skeleton />
					<Skeleton />
				</div>
			</div>
		);
	}

	return (
		<div className="animate-fade-in">
			<PageHeader title={title} subtitle={subtitle} color={color} />

			{error && (
				<div className="bg-red-900/20 border border-red-800/40 rounded-xl p-4 mb-4 flex items-center gap-3 text-sm text-red-400">
					<AlertTriangle size={16} /> {error}
				</div>
			)}

			{data && (
				<>
					<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
						{data.movies !== undefined && <StatCard label="Movies" value={data.movies} color={color} />}
						{data.series !== undefined && <StatCard label="Series" value={data.series} color={color} />}
						{data.artists !== undefined && <StatCard label="Artists" value={data.artists} color={color} />}
						{data.authors !== undefined && <StatCard label="Authors" value={data.authors} color={color} />}
						{data.indexers !== undefined && <StatCard label="Indexers" value={data.indexers} color={color} />}
						{data.applications !== undefined && <StatCard label="Apps" value={data.applications} color={color} />}
						{data.wanted !== undefined && <StatCard label="Wanted" value={data.wanted} color={color} highlight />}
						{data.queue !== undefined && <StatCard label="In Queue" value={data.queue} color={color} />}
						{data.movies_wanted !== undefined && (
							<StatCard label="Movies Missing Subs" value={data.movies_wanted} color={color} />
						)}
						{data.episodes_wanted !== undefined && (
							<StatCard label="Episodes Missing Subs" value={data.episodes_wanted} color={color} />
						)}
						{data.providers !== undefined && <StatCard label="Providers" value={data.providers} color={color} />}
						{data.total_requests !== undefined && (
							<StatCard label="Total Requests" value={data.total_requests} color={color} />
						)}
						{data.pending !== undefined && <StatCard label="Pending" value={data.pending} color={color} highlight />}
					</div>

					{data.disk && data.disk.length > 0 && (
						<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
							<h3 className="flex items-center gap-2 font-semibold text-sm mb-3">
								<HardDrive size={16} /> Disk Space
							</h3>
							<div className="space-y-2">
								{data.disk.map((d, i) => {
									const used = d.totalSpace - d.freeSpace;
									const pct = d.totalSpace > 0 ? (used / d.totalSpace) * 100 : 0;
									return (
										<div key={`disk-${i}`} className="flex items-center gap-3 text-sm">
											<span className="text-zinc-400 w-32 truncate font-mono text-xs">{d.path}</span>
											<div className="flex-1 bg-zinc-800 rounded-full h-2.5">
												<div className={`bg-${color} h-2.5 rounded-full`} style={{ width: `${Math.min(pct, 100)}%` }} />
											</div>
											<span className="text-zinc-500 text-xs font-mono">{pct.toFixed(1)}%</span>
										</div>
									);
								})}
							</div>
						</div>
					)}
				</>
			)}

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<div className="flex items-center justify-between mb-3">
					<h3 className="font-semibold text-sm text-zinc-300">Raw API Response</h3>
					<button
						type="button"
						onClick={() => {
							setLoading(true);
							setError("");
							setTimeout(() => window.location.reload(), 0);
						}}
						className="text-xs text-zinc-500 hover:text-zinc-300 flex items-center gap-1"
					>
						<RefreshCw size={12} /> Refresh
					</button>
				</div>
				<pre className="text-xs text-zinc-400 font-mono whitespace-pre-wrap max-h-64 overflow-y-auto">
					{raw ? JSON.stringify(raw, null, 2) : "No data"}
				</pre>
			</div>
		</div>
	);
}

function PageHeader({ title, subtitle, color }: { title: string; subtitle: string; color: string }) {
	return (
		<div className="flex items-center gap-3 mb-6">
			<Package size={24} className={`text-${color}`} />
			<h2 className="text-2xl font-bold">{title}</h2>
			<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">{subtitle}</span>
		</div>
	);
}

function StatCard({
	label,
	value,
	color,
	highlight,
}: { label: string; value: number; color: string; highlight?: boolean }) {
	return (
		<div className={`bg-zinc-900 border ${highlight ? `border-${color}/30` : "border-zinc-800"} rounded-xl p-5`}>
			<p className="text-xs text-zinc-500 mb-1">{label}</p>
			<p className={`text-3xl font-bold text-${color}`}>{value.toLocaleString()}</p>
		</div>
	);
}

function Skeleton() {
	return (
		<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
			<div className="h-4 bg-zinc-800 rounded w-20 mb-3" />
			<div className="h-8 bg-zinc-800 rounded w-16" />
		</div>
	);
}
