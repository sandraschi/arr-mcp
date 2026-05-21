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
import { type HealthResult, fetchHealth } from "../utils/api";

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
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

	useEffect(() => {
		let mounted = true;

		async function poll() {
			try {
				const h = await fetchHealth();
				if (mounted) {
					setHealth(h.data);
					setLastUpdate(new Date());
					setError("");
				}
			} catch (e) {
				if (mounted) setError(String(e));
			} finally {
				if (mounted) setLoading(false);
			}
		}

		poll();
		const interval = setInterval(poll, 15000);
		return () => {
			mounted = false;
			clearInterval(interval);
		};
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

	const reachableCount = Object.values(health || {}).filter((h) => h.reachable).length;
	const totalCount = Object.keys(health || {}).length;

	return (
		<div className="animate-fade-in">
			<div className="flex items-center justify-between mb-6">
				<h2 className="text-2xl font-bold">Dashboard</h2>
				<div className="flex items-center gap-3">
					{error && (
						<div className="flex items-center gap-1.5 text-xs text-red-400">
							<AlertTriangle size={12} />
							<span>Backend unreachable</span>
						</div>
					)}
					<span className="text-xs text-zinc-500">
						{reachableCount}/{totalCount} reachable
						{lastUpdate && ` · updated ${lastUpdate.toLocaleTimeString()}`}
					</span>
				</div>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
				{services.map((svc) => {
					const h = health?.[svc.key];
					const isReachable = h?.reachable;

					return (
						<div
							key={svc.key}
							className={`bg-zinc-900 border rounded-xl p-5 transition-colors ${
								isReachable ? "border-zinc-700 hover:border-zinc-600" : "border-zinc-800 opacity-60"
							}`}
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
								<div className="space-y-1 text-xs">
									{h?.version && <p className="text-zinc-400">v{h.version}</p>}
									<p className="text-green-500/70">Running</p>
								</div>
							) : (
								<p className="text-xs text-zinc-600">{h?.reason || "not configured"}</p>
							)}
						</div>
					);
				})}
			</div>

			{health && Object.keys(health).length > 0 && (
				<div className="mt-8">
					<h3 className="text-lg font-semibold mb-4">Health JSON</h3>
					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 overflow-x-auto">
						<pre className="text-xs text-zinc-400 font-mono whitespace-pre">{JSON.stringify(health, null, 2)}</pre>
					</div>
				</div>
			)}
		</div>
	);
}
