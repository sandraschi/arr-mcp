import { BarChart3, Calendar, CheckCircle, Puzzle, Search, Send } from "lucide-react";

export default function OrchestratePage() {
	return (
		<div className="animate-fade-in">
			<div className="flex items-center gap-3 mb-6">
				<Puzzle size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Orchestrate</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Cross-Arr Pipeline</span>
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
				<h3 className="font-semibold mb-4">Media Request Pipeline</h3>
				<div className="flex items-center gap-3 text-sm text-zinc-400 mb-6">
					<div className="bg-zinc-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
						<Search size={14} />
						<span>Jellyfin Check</span>
					</div>
					<span className="text-zinc-700">→</span>
					<div className="bg-zinc-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
						<Puzzle size={14} />
						<span>Type Detection</span>
					</div>
					<span className="text-zinc-700">→</span>
					<div className="bg-zinc-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
						<CheckCircle size={14} />
						<span>Queue Check</span>
					</div>
					<span className="text-zinc-700">→</span>
					<div className="bg-zinc-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
						<Send size={14} />
						<span>Add to Arr</span>
					</div>
				</div>
				<p className="text-sm text-zinc-500">
					Say &ldquo;I want to watch Dune&rdquo; → arr-mcp checks Jellyfin first. If not found, it auto-detects the
					media type and routes to Radarr/Sonarr/Lidarr/Readarr. If already in your library, it tells you — no duplicate
					requests.
				</p>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				<QuickAction icon={Send} label="Request Media" desc="Find & queue a title" color="zinc" />
				<QuickAction icon={BarChart3} label="Stack Stats" desc="Consolidated statistics" color="zinc" />
				<QuickAction icon={Calendar} label="Calendar" desc="Unified release calendar" color="zinc" />
			</div>

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

function QuickAction({
	icon: Icon,
	label,
	desc,
	color,
}: {
	icon: typeof Puzzle;
	label: string;
	desc: string;
	color: string;
}) {
	return (
		<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-700 transition-colors cursor-pointer group">
			<div className="flex items-center gap-3">
				<Icon size={20} className="text-zinc-400 group-hover:scale-110 transition-transform" />
				<div>
					<p className="font-medium text-sm">{label}</p>
					<p className="text-xs text-zinc-500 mt-0.5">{desc}</p>
				</div>
			</div>
		</div>
	);
}
