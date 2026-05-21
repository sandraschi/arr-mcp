import { List, Plus, RefreshCw, Search, Tv } from "lucide-react";

export default function SonarrPage() {
	return (
		<div className="animate-fade-in">
			<div className="flex items-center gap-3 mb-6">
				<Tv size={24} className="text-sonarr" />
				<h2 className="text-2xl font-bold">Sonarr</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">TV Series</span>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				<QuickAction icon={Search} label="Series Library" desc="Browse all series" color="sonarr" />
				<QuickAction icon={Plus} label="Add Series" desc="Lookup & add from TVDB" color="sonarr" />
				<QuickAction icon={List} label="Episodes" desc="View episode management" color="sonarr" />
				<QuickAction icon={RefreshCw} label="Import" desc="Scan for downloaded files" color="sonarr" />
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<h3 className="font-semibold mb-3 text-sm text-zinc-300">MCP Tools</h3>
				<div className="space-y-2 text-sm">
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-sonarr">sonarr_series</code>
						<span className="text-zinc-500">— list, lookup, get, add, delete, update</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-sonarr">sonarr_episodes</code>
						<span className="text-zinc-500">— list, get, search, set_monitored</span>
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
	icon: typeof Tv;
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
