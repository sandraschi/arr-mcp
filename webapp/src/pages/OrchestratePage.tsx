import { BarChart3, CheckCircle, Loader2, Puzzle, Search, Send } from "lucide-react";
import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";

interface RequestResult {
	success: boolean;
	message: string;
	pipeline?: string[];
	data?: Record<string, unknown>;
}

export default function OrchestratePage() {
	const [summary, setSummary] = useState<Record<
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
	> | null>(null);
	const [totalWanted, setTotalWanted] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [title, setTitle] = useState("");
	const [mediaType, setMediaType] = useState("");
	const [requesting, setRequesting] = useState(false);
	const [requestError, setRequestError] = useState("");
	const [requestResult, setRequestResult] = useState<RequestResult | null>(null);

	async function submitRequest(e: React.FormEvent) {
		e.preventDefault();
		const trimmed = title.trim();
		if (!trimmed || requesting) return;
		setRequesting(true);
		setRequestError("");
		setRequestResult(null);
		try {
			const result = await apiFetch<RequestResult>("/api/orchestrate/request", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					media_title: trimmed,
					...(mediaType ? { media_type: mediaType } : {}),
				}),
				timeoutMs: 60000,
			});
			setRequestResult(result);
		} catch (err) {
			setRequestError(String(err));
		} finally {
			setRequesting(false);
		}
	}

	useEffect(() => {
		let mounted = true;
		async function poll() {
			try {
				const json = await apiFetch<{ success: boolean; data: Record<string, unknown>; total_wanted?: number }>(
					"/api/orchestrator/summary",
				);
				if (mounted) {
					setSummary(
						json.data as Record<
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
						>,
					);
					setTotalWanted(json.total_wanted || 0);
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
	}, []);

	return (
		<div className="animate-fade-in" data-testid="orchestrate-page">
			<div className="flex items-center gap-3 mb-6">
				<Puzzle size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Orchestrate</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Cross-Arr Pipeline</span>
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6" data-testid="orchestrate-pipeline">
				<h3 className="font-semibold mb-4">Media Request Pipeline</h3>
				<div className="flex flex-wrap items-center gap-2 text-sm text-zinc-400 mb-6">
					<PipelineStep icon={Search} label="Jellyfin Check" />
					<span className="text-zinc-700">→</span>
					<PipelineStep icon={Puzzle} label="Type Detection" />
					<span className="text-zinc-700">→</span>
					<PipelineStep icon={CheckCircle} label="Queue Check" />
					<span className="text-zinc-700">→</span>
					<PipelineStep icon={Send} label="Add to Arr" />
				</div>
				<p className="text-sm text-zinc-500">
					"I want to watch Dune" → checks Jellyfin first. If not in your library, auto-detects the media type and routes
					to Radarr/Sonarr/Lidarr/Readarr. No duplicate requests.
				</p>
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6" data-testid="orchestrate-request">
				<h3 className="font-semibold mb-1">Request media</h3>
				<p className="text-xs text-zinc-500 mb-4">
					Runs the real pipeline: library check → type detection → queue check → add. Takes up to a minute.
				</p>
				<form onSubmit={submitRequest} className="flex flex-col sm:flex-row gap-2">
					<input
						value={title}
						onChange={(e) => setTitle(e.target.value)}
						placeholder="e.g. Dune"
						className="flex-1 bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500"
						data-testid="orchestrate-title"
					/>
					<select
						value={mediaType}
						onChange={(e) => setMediaType(e.target.value)}
						className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 [color-scheme:dark]"
						data-testid="orchestrate-type"
					>
						<option value="">Auto-detect type</option>
						<option value="movie">Movie</option>
						<option value="series">Series</option>
						<option value="album">Album</option>
						<option value="book">Book</option>
					</select>
					<button
						type="submit"
						disabled={!title.trim() || requesting}
						className="flex items-center justify-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-zinc-100 hover:bg-white text-zinc-900 font-medium disabled:opacity-50 transition-colors"
						data-testid="orchestrate-submit"
					>
						{requesting ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
						{requesting ? "Working…" : "Request"}
					</button>
				</form>
				{requestError && (
					<p className="text-xs text-red-400 mt-3" data-testid="orchestrate-request-error">
						{requestError}
					</p>
				)}
				{requestResult && (
					<div className="mt-4 border-t border-zinc-800 pt-4" data-testid="orchestrate-result">
						<p className={`text-sm ${requestResult.success ? "text-green-400" : "text-yellow-400"}`}>
							{requestResult.message}
						</p>
						{requestResult.pipeline && requestResult.pipeline.length > 0 && (
							<div className="flex flex-wrap gap-1.5 mt-2">
								{requestResult.pipeline.map((step) => (
									<span key={step} className="text-xs font-mono bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded">
										{step}
									</span>
								))}
							</div>
						)}
					</div>
				)}
			</div>

			{error && (
				<div className="bg-red-900/20 border border-red-800/40 rounded-xl p-4 mb-4 text-sm text-red-400">{error}</div>
			)}

			{loading ? (
				<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
					<Skeleton />
					<Skeleton />
					<Skeleton />
					<Skeleton />
				</div>
			) : (
				<>
					<div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
						{summary &&
							Object.entries(summary).map(([name, s]) => (
								<div
									key={name}
									className={`bg-zinc-900 border rounded-xl p-5 ${s.enabled ? "border-zinc-800" : "border-zinc-800 opacity-50"}`}
								>
									<p className="text-xs text-zinc-500 capitalize mb-1">{name}</p>
									{s.enabled ? (
										<>
											<p className="text-2xl font-bold text-zinc-200">
												{(s.movies ?? s.series ?? s.artists ?? s.authors ?? 0).toLocaleString()}
											</p>
											{s.wanted > 0 && <p className="text-xs text-yellow-500 mt-1">{s.wanted} wanted</p>}
										</>
									) : (
										<p className="text-xs text-zinc-600">Not configured</p>
									)}
									{s.error && <p className="text-xs text-red-400 mt-1">{s.error}</p>}
								</div>
							))}
					</div>

					<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4" data-testid="orchestrate-overview">
						<h3 className="flex items-center gap-2 font-semibold text-sm mb-3">
							<BarChart3 size={16} /> Stack Overview
						</h3>
						<div className="text-3xl font-bold text-zinc-200 mb-1">{totalWanted.toLocaleString()}</div>
						<p className="text-sm text-zinc-500">total wanted/missing across all services</p>
					</div>
				</>
			)}

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<h3 className="font-semibold mb-3 text-sm text-zinc-300">MCP Tools</h3>
				<div className="space-y-2 text-sm">
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-zinc-300">arr_orchestrate</code>
						<span className="text-zinc-500">— request, status, check_jellyfin, queue</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-zinc-300">arr_calendar</code>
						<span className="text-zinc-500">— upcoming, today, week, range</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-zinc-300">arr_stats</code>
						<span className="text-zinc-500">— summary, disk, queues, history</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-zinc-300">arr_health</code>
						<span className="text-zinc-500">— stack-wide health probe</span>
					</div>
				</div>
			</div>
		</div>
	);
}

function PipelineStep({ icon: Icon, label }: { icon: typeof Puzzle; label: string }) {
	return (
		<div className="bg-zinc-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
			<Icon size={14} />
			<span>{label}</span>
		</div>
	);
}

function Skeleton() {
	return (
		<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
			<div className="h-4 bg-zinc-800 rounded w-16 mb-3" />
			<div className="h-8 bg-zinc-800 rounded w-12" />
		</div>
	);
}
