import { Activity, Globe, History, Link, RefreshCw, Search } from "lucide-react";

export default function ProwlarrPage() {
	return (
		<div className="animate-fade-in">
			<div className="flex items-center gap-3 mb-6">
				<Search size={24} className="text-prowlarr" />
				<h2 className="text-2xl font-bold">Prowlarr</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Indexer Backbone</span>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				<QuickAction icon={Globe} label="Indexers" desc="Manage Usenet & Torrent indexers" color="prowlarr" />
				<QuickAction icon={Search} label="Unified Search" desc="Search across all indexers" color="prowlarr" />
				<QuickAction icon={Link} label="Applications" desc="Synced Radarr/Sonarr/Lidarr" color="prowlarr" />
				<QuickAction icon={History} label="History" desc="Grab & search history" color="prowlarr" />
				<QuickAction icon={RefreshCw} label="Sync All" desc="Sync indexers to all apps" color="prowlarr" />
				<QuickAction icon={Activity} label="Stats" desc="Indexer statistics" color="prowlarr" />
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<h3 className="font-semibold mb-3 text-sm text-zinc-300">MCP Tools</h3>
				<div className="space-y-2 text-sm">
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-prowlarr">prowlarr_indexers</code>
						<span className="text-zinc-500">— list, get, add, update, delete, test, schema</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-prowlarr">prowlarr_search</code>
						<span className="text-zinc-500">— unified search with category filtering</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-prowlarr">prowlarr_applications</code>
						<span className="text-zinc-500">— list, get, sync, sync_all, test</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-prowlarr">prowlarr_history</code>
						<span className="text-zinc-500">— list, since, by_indexer</span>
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
	icon: typeof Search;
	label: string;
	desc: string;
	color: string;
}) {
	return (
		<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-700 transition-colors cursor-pointer group">
			<div className="flex items-center gap-3">
				<Icon size={20} className={`text-${color} group-hover:scale-110 transition-transform`} />
				<div>
					<p className="font-medium text-sm">{label}</p>
					<p className="text-xs text-zinc-500 mt-0.5">{desc}</p>
				</div>
			</div>
		</div>
	);
}
