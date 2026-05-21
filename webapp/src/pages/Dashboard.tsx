import {
	AlertTriangle,
	BookOpen,
	CheckCircle,
	Film,
	Music,
	Search,
	Subtitles,
	Tv,
	UserCheck,
	XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { type HealthResult, fetchHealth, fetchStats } from "../utils/api";

interface ServiceCard {
	key: string;
	label: string;
	icon: typeof Film;
	color: string;
}

const services: ServiceCard[] = [
	{ key: "radarr", label: "Radarr", icon: Film, color: "radarr" },
	{ key: "sonarr", label: "Sonarr", icon: Tv, color: "sonarr" },
	{ key: "lidarr", label: "Lidarr", icon: Music, color: "lidarr" },
	{ key: "prowlarr", label: "Prowlarr", icon: Search, color: "prowlarr" },
	{ key: "readarr", label: "Readarr", icon: BookOpen, color: "readarr" },
	{ key: "overseerr", label: "Overseerr", icon: UserCheck, color: "overseerr" },
	{ key: "bazarr", label: "Bazarr", icon: Subtitles, color: "bazarr" },
];

export default function Dashboard() {
	const [health, setHealth] = useState<Record<string, HealthResult> | null>(null);
	const [stats, setStats] = useState<Record<string, Record<string, unknown>> | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		async function load() {
			try {
				const [h, s] = await Promise.all([fetchHealth(), fetchStats("summary")]);
				setHealth(h.data);
				setStats(s.data);
			} catch (e) {
				setError(String(e));
			} finally {
				setLoading(false);
			}
		}
		load();
	}, []);

	if (loading) {
		return (
			<div className="animate-fade-in">
				<h2 className="text-2xl font-bold mb-6">Dashboard</h2>
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
						<div className="h-4 bg-zinc-800 rounded w-20 mb-3" />
						<div className="h-3 bg-zinc-800 rounded w-32" />
					</div>
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
						<div className="h-4 bg-zinc-800 rounded w-20 mb-3" />
						<div className="h-3 bg-zinc-800 rounded w-32" />
					</div>
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
						<div className="h-4 bg-zinc-800 rounded w-20 mb-3" />
						<div className="h-3 bg-zinc-800 rounded w-32" />
					</div>
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
						<div className="h-4 bg-zinc-800 rounded w-20 mb-3" />
						<div className="h-3 bg-zinc-800 rounded w-32" />
					</div>
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
						<div className="h-4 bg-zinc-800 rounded w-20 mb-3" />
						<div className="h-3 bg-zinc-800 rounded w-32" />
					</div>
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
						<div className="h-4 bg-zinc-800 rounded w-20 mb-3" />
						<div className="h-3 bg-zinc-800 rounded w-32" />
					</div>
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
						<div className="h-4 bg-zinc-800 rounded w-20 mb-3" />
						<div className="h-3 bg-zinc-800 rounded w-32" />
					</div>
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className="animate-fade-in">
				<h2 className="text-2xl font-bold mb-6">Dashboard</h2>
				<div className="bg-red-900/20 border border-red-800/40 rounded-xl p-6 text-red-400 flex items-center gap-3">
					<AlertTriangle size={20} />
					<div>
						<p className="font-medium">Failed to load dashboard</p>
						<p className="text-sm text-red-400/70 mt-1">{error}</p>
					</div>
				</div>
			</div>
		);
	}

	const reachableCount = Object.values(health || {}).filter((h) => h.reachable).length;
	const totalCount = Object.keys(health || {}).length;

	return (
		<div className="animate-fade-in">
			<div className="flex items-center justify-between mb-6">
				<h2 className="text-2xl font-bold">Dashboard</h2>
				<span className="text-sm text-zinc-400">
					{reachableCount}/{totalCount} services reachable
				</span>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
				{services.map((svc) => {
					const h = health?.[svc.key];
					const s = stats?.[svc.key] as Record<string, unknown> | undefined;
					const isReachable = h?.reachable;
					const version = h?.version;

					const colorVar = `var(--tw-${svc.color})`;
					const dimVar = `var(--tw-${svc.color}-dim)`;

					return (
						<div
							key={svc.key}
							className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-colors"
						>
							<div className="flex items-center justify-between mb-3">
								<div className="flex items-center gap-2.5">
									<svc.icon size={20} className={`text-${svc.color}`} />
									<h3 className="font-semibold text-sm">{svc.label}</h3>
								</div>
								{isReachable ? (
									<CheckCircle size={16} className={`text-${svc.color}`} />
								) : (
									<XCircle size={16} className="text-zinc-600" />
								)}
							</div>
							{isReachable ? (
								<div className="space-y-1 text-xs text-zinc-500">
									{version && <p>v{version}</p>}
									{s && s.wanted !== undefined && (
										<p>
											<span className="text-zinc-400">{String(s.wanted)}</span> wanted
										</p>
									)}
								</div>
							) : (
								<p className="text-xs text-zinc-600">{h?.reason || "not configured"}</p>
							)}
						</div>
					);
				})}
			</div>

			{stats && (
				<div className="mt-8">
					<h3 className="text-lg font-semibold mb-4">Stack Summary</h3>
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 overflow-x-auto">
						<pre className="text-xs text-zinc-400 font-mono whitespace-pre">{JSON.stringify(stats, null, 2)}</pre>
					</div>
				</div>
			)}
		</div>
	);
}
