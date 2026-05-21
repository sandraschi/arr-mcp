import {
	Activity,
	Book,
	BookOpen,
	ExternalLink,
	Film,
	HelpCircle,
	Music,
	Puzzle,
	Search as SearchIcon,
	Subtitles,
	Terminal,
	Tv,
	UserCheck,
} from "lucide-react";

interface ToolRef {
	name: string;
	operations: string;
	description: string;
	color: string;
}

const tools: ToolRef[] = [
	{
		name: "radarr_movies",
		operations: "list, lookup, get, add, delete, update, import",
		description: "Manage Radarr movies — browse library, search TMDB, add/remove movies, scan imports.",
		color: "radarr",
	},
	{
		name: "sonarr_series",
		operations: "list, lookup, get, add, delete, update",
		description: "Manage Sonarr TV series — browse library, search TVDB, add/remove series.",
		color: "sonarr",
	},
	{
		name: "sonarr_episodes",
		operations: "list, get, search, set_monitored",
		description: "Manage Sonarr episodes — list by series, trigger search, toggle monitoring.",
		color: "sonarr",
	},
	{
		name: "lidarr_artists",
		operations: "list, lookup, get, add, delete, update",
		description: "Manage Lidarr artists — browse library, search MusicBrainz, add/remove artists.",
		color: "lidarr",
	},
	{
		name: "lidarr_albums",
		operations: "list, get, lookup, set_monitored",
		description: "Manage Lidarr albums — list by artist, search, toggle monitoring per album.",
		color: "lidarr",
	},
	{
		name: "prowlarr_indexers",
		operations: "list, get, add, update, delete, test, test_all, schema",
		description: "Manage Prowlarr indexers — CRUD for Usenet/Torrent indexers, test connectivity.",
		color: "prowlarr",
	},
	{
		name: "prowlarr_search",
		operations: "query (unified)",
		description: "Unified search across ALL Prowlarr indexers with category filtering.",
		color: "prowlarr",
	},
	{
		name: "prowlarr_applications",
		operations: "list, get, sync, sync_all, test",
		description: "Manage synced Radarr/Sonarr/Lidarr apps — sync indexer configs.",
		color: "prowlarr",
	},
	{
		name: "prowlarr_history",
		operations: "list, since, by_indexer",
		description: "Query Prowlarr grab/search history by date or indexer.",
		color: "prowlarr",
	},
	{
		name: "readarr_authors",
		operations: "list, lookup, get, add, delete, update",
		description: "Manage Readarr authors — browse library, search, add/remove authors.",
		color: "readarr",
	},
	{
		name: "readarr_books",
		operations: "list, get, lookup, set_monitored",
		description: "Manage Readarr books — list by author, search, toggle monitoring.",
		color: "readarr",
	},
	{
		name: "overseerr_requests",
		operations: "list, get, create, approve, decline, delete, count, pending",
		description: "Manage Overseerr media requests — full request lifecycle management.",
		color: "overseerr",
	},
	{
		name: "overseerr_search",
		operations: "query",
		description: "Search Overseerr/TMDB for movies, TV shows, and people.",
		color: "overseerr",
	},
	{
		name: "overseerr_users",
		operations: "list, get, requests",
		description: "Manage Overseerr users and view their request history.",
		color: "overseerr",
	},
	{
		name: "bazarr_subtitles",
		operations: "wanted, search, download, history, providers, languages",
		description: "Manage Bazarr subtitles — search, download, view wanted list and history.",
		color: "bazarr",
	},
	{
		name: "arr_orchestrate",
		operations: "request, status, check_jellyfin, queue",
		description: "Cross-arr orchestration — request media with Jellyfin check + auto-routing.",
		color: "zinc",
	},
	{
		name: "arr_calendar",
		operations: "upcoming, today, week, range",
		description: "Unified release calendar across Radarr, Sonarr, Lidarr, and Readarr.",
		color: "zinc",
	},
	{
		name: "arr_stats",
		operations: "summary, disk, queues, history",
		description: "Consolidated statistics across the entire *arr stack.",
		color: "zinc",
	},
	{
		name: "arr_health",
		operations: "all, radarr, sonarr, lidarr, prowlarr, readarr, overseerr, bazarr",
		description: "Stack-wide health probe — checks system status per service.",
		color: "zinc",
	},
];

export default function HelpPage() {
	return (
		<div className="animate-fade-in max-w-3xl">
			<div className="flex items-center gap-3 mb-6">
				<HelpCircle size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Help</h2>
			</div>

			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-3">
					<Book size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">What is arr-mcp?</h3>
				</div>
				<p className="text-sm text-zinc-400 leading-relaxed">
					arr-mcp is a FastMCP 3.3 server that wraps the complete *arr automation stack under a single MCP interface.
					One server manages Radarr (Movies), Sonarr (TV), Lidarr (Music), Prowlarr (Indexers), Readarr (Books),
					Overseerr (Requests), and Bazarr (Subtitles). Each service is independently optional and configurable via{" "}
					<code className="bg-zinc-800 px-1.5 py-0.5 rounded text-xs">.env</code>.
				</p>
			</section>

			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-3">
					<Terminal size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Quick Start</h3>
				</div>
				<div className="bg-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-400 space-y-1">
					<div>
						<span className="text-zinc-600"># Clone and configure</span>
					</div>
					<div>git clone https://github.com/sandraschi/arr-mcp</div>
					<div>cd arr-mcp</div>
					<div>cp .env.example .env</div>
					<div>
						<span className="text-zinc-600"># Edit .env with your *arr URLs and API keys</span>
					</div>
					<div>uv sync</div>
					<div>uv run arr-mcp</div>
				</div>
			</section>

			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-3">
					<Activity size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">MCP Tool Reference ({tools.length} tools)</h3>
				</div>
				<div className="space-y-2">
					{tools.map((tool) => (
						<div key={tool.name} className="bg-zinc-800 rounded-lg p-3">
							<div className="flex items-center gap-2 mb-1">
								<code className={`text-xs font-mono px-1.5 py-0.5 rounded bg-zinc-700 text-${tool.color}`}>
									{tool.name}
								</code>
							</div>
							<p className="text-xs text-zinc-500 mb-1">{tool.description}</p>
							<p className="text-xs text-zinc-600 font-mono">Operations: {tool.operations}</p>
						</div>
					))}
				</div>
			</section>

			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<div className="flex items-center gap-2 mb-3">
					<ExternalLink size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Links</h3>
				</div>
				<div className="space-y-2 text-sm">
					<a
						href="https://github.com/sandraschi/arr-mcp"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> GitHub Repository
					</a>
					<a
						href="https://wiki.servarr.com"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> Servarr Wiki
					</a>
					<a
						href="https://radarr.video"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> Radarr
					</a>
					<a
						href="https://sonarr.tv"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> Sonarr
					</a>
				</div>
			</section>
		</div>
	);
}
