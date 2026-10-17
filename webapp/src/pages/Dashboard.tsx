import {
	AlertTriangle,
	ArrowRight,
	BookOpen,
	CheckCircle,
	Container,
	Film,
	ListVideo,
	Loader2,
	Music,
	Play,
	Search,
	Send,
	Subtitles,
	Tv,
	UserCheck,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type HealthResult, apiFetch, fetchHealth } from "../utils/api";
import { textColor } from "../utils/colors";

interface ServiceCard {
	key: string;
	label: string;
	icon: typeof Film;
	color: string;
	route: string;
}

const services: ServiceCard[] = [
	{ key: "radarr", label: "Radarr", icon: Film, color: "radarr", route: "/radarr" },
	{ key: "sonarr", label: "Sonarr", icon: Tv, color: "sonarr", route: "/sonarr" },
	{ key: "lidarr", label: "Lidarr", icon: Music, color: "lidarr", route: "/lidarr" },
	{ key: "prowlarr", label: "Prowlarr", icon: Search, color: "prowlarr", route: "/prowlarr" },
	{ key: "readarr", label: "Readarr", icon: BookOpen, color: "readarr", route: "/readarr" },
	{ key: "overseerr", label: "Overseerr", icon: UserCheck, color: "overseerr", route: "/overseerr" },
	{ key: "bazarr", label: "Bazarr", icon: Subtitles, color: "bazarr", route: "/bazarr" },
];

interface OrchestratorSummary {
	data: Record<
		string,
		{
			enabled: boolean;
			movies?: number;
			series?: number;
			artists?: number;
			authors?: number;
			wanted: number;
			error?: string;
		}
	>;
	total_wanted?: number;
}

interface FleetSibling {
	name: string;
	label: string;
	role: string;
	reachable: boolean;
	frontend_url: string;
	backend_url: string;
}

interface DockerState {
	available: boolean;
	reason?: string;
	containers: {
		name: string;
		image: string;
		service: string;
		ports: string;
		state: string;
		host_port: number | null;
	}[];
}

export default function Dashboard() {
	const [health, setHealth] = useState<Record<string, HealthResult> | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
	const [orch, setOrch] = useState<OrchestratorSummary | null>(null);
	const [fleet, setFleet] = useState<FleetSibling[] | null>(null);
	const [docker, setDocker] = useState<DockerState | null>(null);
	const [startingAll, setStartingAll] = useState(false);
	const [startAllStatus, setStartAllStatus] = useState("");

	async function refreshDocker() {
		try {
			const d = await apiFetch<{ success: boolean; data: DockerState }>("/api/docker");
			setDocker(d.data);
		} catch {
			setDocker(null);
		}
	}

	async function startAllMissing() {
		if (startingAll) return;
		const running = new Set((docker?.containers ?? []).map((c) => c.service));
		const missing = services.map((s) => s.key).filter((k) => !running.has(k));
		if (missing.length === 0) return;
		setStartingAll(true);
		setStartAllStatus("");
		try {
			for (const service of missing) {
				setStartAllStatus(`Starting ${service}… (${missing.indexOf(service) + 1}/${missing.length})`);
				const result = await apiFetch<{ success: boolean; message: string }>("/api/docker/start", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ service }),
					timeoutMs: 200000,
				});
				if (!result.success) {
					setStartAllStatus(`Stopped: ${service}: ${result.message}`);
					break;
				}
				await refreshDocker();
			}
			setStartAllStatus((s) => (s.startsWith("Stopped") ? s : "All containers started — grab API keys next."));
		} catch (err) {
			setStartAllStatus(`Stopped: ${String(err)}`);
		} finally {
			setStartingAll(false);
			await refreshDocker();
		}
	}

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
			try {
				const o = await apiFetch<OrchestratorSummary>("/api/orchestrator/summary");
				if (mounted) setOrch(o);
			} catch {
				/* KPIs stay empty when the backend is down */
			}
		}
		async function loadOnce() {
			try {
				const f = await apiFetch<{ success: boolean; siblings: FleetSibling[] }>("/api/fleet");
				if (mounted) setFleet(f.siblings);
			} catch {
				if (mounted) setFleet(null);
			}
			try {
				const d = await apiFetch<{ success: boolean; data: DockerState }>("/api/docker");
				if (mounted) setDocker(d.data);
			} catch {
				if (mounted) setDocker(null);
			}
		}

		poll();
		loadOnce();
		const interval = setInterval(poll, 15000);
		return () => {
			mounted = false;
			clearInterval(interval);
		};
	}, []);

	if (loading) {
		return (
			<div className="animate-fade-in" data-testid="dashboard-loading">
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
	const totalItems = orch
		? Object.values(orch.data).reduce((acc, s) => acc + (s.movies ?? s.series ?? s.artists ?? s.authors ?? 0), 0)
		: 0;
	const totalWanted = orch?.total_wanted ?? 0;

	return (
		<div className="animate-fade-in" data-testid="dashboard">
			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-6" data-testid="dashboard-hero">
				<h1 className="text-xl font-bold">*arr stack control panel</h1>
				<p className="text-sm text-zinc-400 mt-1">
					One dashboard for Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr and Bazarr. Cards below show live
					reachability (polled every 15s). Missing a service? Copy{" "}
					<code className="font-mono text-zinc-300">.env.example</code> to{" "}
					<code className="font-mono text-zinc-300">.env</code>, add URL + API key, restart the backend. Use Orchestrate
					to request a title — Jellyfin/Plex/Emby are checked first.
				</p>
				<div className="flex flex-wrap gap-2 mt-4">
					<Link
						to="/orchestrate"
						className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-zinc-100 text-zinc-900 font-medium hover:bg-white transition-colors"
						data-testid="dashboard-request"
					>
						<Send size={12} /> Request a title
					</Link>
					<Link
						to="/logger"
						className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors"
						data-testid="dashboard-logs"
					>
						<ListVideo size={12} /> Live logs
					</Link>
					{reachableCount === 0 && !loading && (
						<Link
							to="/help"
							className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-red-700 hover:bg-red-600 text-white font-medium transition-colors"
							data-testid="onboarding-cue"
						>
							Connect your first service <ArrowRight size={12} />
						</Link>
					)}
				</div>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6" data-testid="dashboard-kpis">
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
					<p className="text-xs text-zinc-500 mb-1">Library items</p>
					<p className="text-3xl font-bold text-zinc-100" data-testid="kpi-items">
						{totalItems.toLocaleString()}
					</p>
					<p className="text-xs text-zinc-600 mt-1">movies + series + artists + authors</p>
				</div>
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
					<p className="text-xs text-zinc-500 mb-1">Wanted / missing</p>
					<p className="text-3xl font-bold text-yellow-400" data-testid="kpi-wanted">
						{totalWanted.toLocaleString()}
					</p>
					<p className="text-xs text-zinc-600 mt-1">across all configured arrs</p>
				</div>
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
					<p className="text-xs text-zinc-500 mb-1">Services reachable</p>
					<p className="text-3xl font-bold text-zinc-100" data-testid="kpi-reachable">
						{reachableCount}
						<span className="text-lg text-zinc-500">/{totalCount}</span>
					</p>
					<p className="text-xs text-zinc-600 mt-1">
						{lastUpdate ? `updated ${lastUpdate.toLocaleTimeString()}` : "polling…"}
					</p>
				</div>
			</div>
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
									<svc.icon size={20} className={textColor(svc.color)} />
									<h3 className="font-semibold text-sm">{svc.label}</h3>
								</div>
								{isReachable ? (
									<CheckCircle size={16} className={textColor(svc.color)} />
								) : (
									<span className="text-xs text-zinc-600">not configured</span>
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
							<div className="mt-3">
								{isReachable ? (
									<Link
										to={svc.route}
										className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-100 transition-colors"
									>
										Open {svc.label} <ArrowRight size={12} />
									</Link>
								) : (
									<Link
										to={svc.route}
										className="inline-flex items-center gap-1 text-xs text-yellow-500/90 hover:text-yellow-400 transition-colors"
									>
										Set up {svc.label} <ArrowRight size={12} />
									</Link>
								)}
							</div>
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

			{docker?.available && (
				<div className="mt-8" data-testid="dashboard-docker">
					<div className="flex items-center justify-between mb-1">
						<h3 className="text-lg font-semibold">Detected containers</h3>
						{services.some((s) => !(docker.containers ?? []).some((c) => c.service === s.key)) && (
							<button
								type="button"
								onClick={startAllMissing}
								disabled={startingAll}
								className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-green-700 hover:bg-green-600 text-white font-medium disabled:opacity-50 transition-colors"
								data-testid="start-all-containers"
							>
								{startingAll ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
								{startingAll ? "Starting…" : "Start all missing"}
							</button>
						)}
					</div>
					<p className="text-xs text-zinc-500 mb-4">
						Found via <span className="font-mono">docker ps</span> — a running container still needs its API key in{" "}
						<span className="font-mono">.env</span> before its card turns green.
					</p>
					{startAllStatus && (
						<p className="text-xs text-zinc-400 mb-4" data-testid="start-all-status">
							{startAllStatus}
						</p>
					)}
					{docker.containers.length === 0 && (
						<p className="text-xs text-zinc-600 mb-4">
							No stack containers running yet — Start all missing pulls and starts all seven.
						</p>
					)}
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
						{docker.containers.map((c) => (
							<div key={c.name} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center gap-3">
								<Container size={18} className="text-green-500/80 shrink-0" />
								<div className="min-w-0">
									<p className="text-sm font-medium truncate">{c.name}</p>
									<p className="text-xs text-zinc-500 font-mono truncate">{c.image}</p>
									<p className="text-xs text-zinc-500">
										{c.state}
										{c.host_port != null && <span className="font-mono"> · :{c.host_port}</span>}
										<span className="font-mono"> → {c.service}</span>
									</p>
								</div>
							</div>
						))}
					</div>
				</div>
			)}

			{fleet && fleet.length > 0 && (
				<div className="mt-8" data-testid="dashboard-fleet">
					<h3 className="text-lg font-semibold mb-1">Fleet media servers</h3>
					<p className="text-xs text-zinc-500 mb-4">
						arr-mcp acquires media; these siblings own libraries and playback. Reachability is probed live.
					</p>
					<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
						{fleet.map((s) => (
							<div key={s.name} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
								<div className="flex items-center justify-between mb-1">
									<p className="text-sm font-medium">{s.label}</p>
									<span
										className={`text-xs px-2 py-0.5 rounded ${
											s.reachable ? "bg-green-900/40 text-green-300" : "bg-zinc-800 text-zinc-500"
										}`}
									>
										{s.reachable ? "reachable" : "not running"}
									</span>
								</div>
								<p className="text-xs text-zinc-500 mb-3">{s.role}</p>
								{s.reachable && (
									<a
										href={s.frontend_url}
										target="_blank"
										rel="noopener noreferrer"
										className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-100 transition-colors"
									>
										Open {s.label} dashboard <ArrowRight size={12} />
									</a>
								)}
							</div>
						))}
					</div>
				</div>
			)}
		</div>
	);
}
