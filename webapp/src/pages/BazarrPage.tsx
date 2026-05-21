import { Download, Globe, History, Languages, Search, Subtitles } from "lucide-react";

export default function BazarrPage() {
	return (
		<div className="animate-fade-in">
			<div className="flex items-center gap-3 mb-6">
				<Subtitles size={24} className="text-bazarr" />
				<h2 className="text-2xl font-bold">Bazarr</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Subtitles</span>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				<QuickAction icon={Search} label="Wanted" desc="Missing subtitles" color="bazarr" />
				<QuickAction icon={Globe} label="Search" desc="Search for subtitles" color="bazarr" />
				<QuickAction icon={Download} label="Download" desc="Download subtitles" color="bazarr" />
				<QuickAction icon={History} label="History" desc="Download history" color="bazarr" />
				<QuickAction icon={Globe} label="Providers" desc="Subtitle providers" color="bazarr" />
				<QuickAction icon={Languages} label="Languages" desc="Language profiles" color="bazarr" />
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-6">
				<h3 className="font-semibold mb-3 text-sm text-zinc-300">MCP Tools</h3>
				<div className="space-y-2 text-sm">
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-bazarr">bazarr_subtitles</code>
						<span className="text-zinc-500">— wanted, search, download, history, providers, languages</span>
					</div>
				</div>
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<h3 className="font-semibold mb-3 text-sm text-zinc-300">Jellyfin RAG Feed</h3>
				<p className="text-sm text-zinc-400">
					Bazarr subtitle data feeds into jellyfin-mcp's RAG pipeline for downstream subtitle quality analysis and
					language availability tracking.
				</p>
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
	icon: typeof Subtitles;
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
