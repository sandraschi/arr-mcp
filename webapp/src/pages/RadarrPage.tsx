import { Film, FolderOpen, HardDrive, Plus, RefreshCw, Search, Trash2 } from "lucide-react";

export default function RadarrPage() {
	return (
		<div className="animate-fade-in">
			<div className="flex items-center gap-3 mb-6">
				<Film size={24} className="text-radarr" />
				<h2 className="text-2xl font-bold">Radarr</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Movies</span>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				<QuickAction icon={Search} label="Movie Library" desc="Browse all movies" color="radarr" />
				<QuickAction icon={Plus} label="Add Movie" desc="Lookup & add from TMDB" color="radarr" />
				<QuickAction icon={RefreshCw} label="Import" desc="Scan for downloaded files" color="radarr" />
				<QuickAction icon={FolderOpen} label="Collections" desc="View movie collections" color="radarr" />
				<QuickAction icon={HardDrive} label="Disk Space" desc="Check storage" color="radarr" />
				<QuickAction icon={Trash2} label="Blocklist" desc="Manage blocked releases" color="radarr" />
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<h3 className="font-semibold mb-3 text-sm text-zinc-300">MCP Tools</h3>
				<div className="space-y-2 text-sm">
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-radarr">radarr_movies</code>
						<span className="text-zinc-500">— list, lookup, get, add, delete, update, import</span>
					</div>
					<div className="text-xs text-zinc-600 mt-3">
						Use the MCP client to interact with these tools. The webapp provides read-only monitoring.
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
	icon: typeof Film;
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
