import {
	Activity,
	ArrowRight,
	Book,
	Box,
	ExternalLink,
	HelpCircle,
	Key,
	Monitor,
	Server,
	Terminal,
} from "lucide-react";
import { useState } from "react";

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

interface ServiceGuide {
	name: string;
	port: number;
	description: string;
	apiKeyPath: string;
	installSteps: string[];
}

const serviceGuides: ServiceGuide[] = [
	{
		name: "Radarr",
		port: 7878,
		description: "Movie collection manager — automates movie downloads via Usenet/BitTorrent.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Docker: docker run -d --name=radarr -p 7878:7878 -v /path/to/config:/config -v /path/to/movies:/movies lscr.io/linuxserver/radarr:latest",
			"Windows: Download installer from https://radarr.video",
			"Linux: Use your package manager or the install script from https://wiki.servarr.com/radarr/installation",
			"First launch: open http://localhost:7878, configure media management, add a download client, add indexers via Prowlarr",
		],
	},
	{
		name: "Sonarr",
		port: 8989,
		description: "TV series collection manager — automates episode downloads.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Docker: docker run -d --name=sonarr -p 8989:8989 -v /path/to/config:/config -v /path/to/tv:/tv lscr.io/linuxserver/sonarr:latest",
			"Windows: Download installer from https://sonarr.tv",
			"First launch: open http://localhost:8989, add root folder, connect Prowlarr for indexers",
		],
	},
	{
		name: "Lidarr",
		port: 8686,
		description: "Music collection manager — automates album downloads via Usenet/BitTorrent.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Docker: docker run -d --name=lidarr -p 8686:8686 -v /path/to/config:/config -v /path/to/music:/music lscr.io/linuxserver/lidarr:latest",
			"First launch: open http://localhost:8686, add root folder, connect to MusicBrainz, add download client",
		],
	},
	{
		name: "Prowlarr",
		port: 9696,
		description: "Indexer manager — central hub for managing Usenet/Torrent indexers across the *arr stack.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Docker: docker run -d --name=prowlarr -p 9696:9696 -v /path/to/config:/config lscr.io/linuxserver/prowlarr:latest",
			"First launch: open http://localhost:9696, add indexers, add Radarr/Sonarr/Lidarr as applications, sync",
		],
	},
	{
		name: "Readarr",
		port: 8787,
		description: "Book collection manager — automates ebook/audiobook downloads.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Docker: docker run -d --name=readarr -p 8787:8787 -v /path/to/config:/config -v /path/to/books:/books lscr.io/linuxserver/readarr:develop",
			"Note: Readarr is in active development — use the :develop tag. Book metadata comes from Goodreads/Google Books.",
		],
	},
	{
		name: "Overseerr",
		port: 5055,
		description: "Media request & discovery — user-friendly UI for requesting movies and TV shows.",
		apiKeyPath: "Settings → General → API Key (or use the setup wizard)",
		installSteps: [
			"Docker: docker run -d --name=overseerr -p 5055:5055 -v /path/to/config:/app/config sctx/overseerr:latest",
			"First launch: open http://localhost:5055, configure Radarr + Sonarr connections, set up Plex/Jellyfin",
			"Note: Overseerr API key is generated during setup. Find it in Settings → General.",
		],
	},
	{
		name: "Bazarr",
		port: 6767,
		description: "Subtitle manager — automatically downloads subtitles for movies and TV shows.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Docker: docker run -d --name=bazarr -p 6767:6767 -v /path/to/config:/config -v /path/to/movies:/movies -v /path/to/tv:/tv lscr.io/linuxserver/bazarr:latest",
			"First launch: open http://localhost:6767, connect Sonarr + Radarr, add subtitle providers (OpenSubtitles, etc.)",
		],
	},
];

export default function HelpPage() {
	const [expandedService, setExpandedService] = useState<string | null>(null);
	const [showToolRef, setShowToolRef] = useState(false);

	return (
		<div className="animate-fade-in max-w-3xl">
			<div className="flex items-center gap-3 mb-6">
				<HelpCircle size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Help</h2>
			</div>

			{/* What is arr-mcp */}
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

			{/* Quick Start */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-3">
					<Terminal size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Quick Start</h3>
				</div>
				<div className="bg-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-400 space-y-1">
					<div>
						<span className="text-zinc-600"># 1. Clone and configure</span>
					</div>
					<div>git clone https://github.com/sandraschi/arr-mcp</div>
					<div>cd arr-mcp</div>
					<div>cp .env.example .env</div>
					<div>
						<span className="text-zinc-600"># 2. Edit .env with your *arr URLs and API keys (see below)</span>
					</div>
					<div>uv sync</div>
					<div>uv run arr-mcp</div>
					<div className="mt-2">
						<span className="text-zinc-600"># 3. Start the webapp (separate terminal)</span>
					</div>
					<div>cd webapp</div>
					<div>npm install</div>
					<div>npm run dev</div>
					<div className="mt-2">
						<span className="text-zinc-600"># Or start everything with Docker Compose (see below)</span>
					</div>
					<div>docker compose up -d</div>
					<div>
						cp .env.example .env <span className="text-zinc-600"># then edit with localhost URLs</span>
					</div>
					<div>uv run arr-mcp</div>
				</div>
			</section>

			{/* Docker Compose */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-3">
					<Box size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Docker Compose — Full *Arr Stack</h3>
				</div>
				<p className="text-sm text-zinc-400 mb-3">
					The repo includes a <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-xs">docker-compose.yml</code> that
					spins up all 8 services (Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr, Bazarr, Jellyfin) with proper
					volume mounts.
				</p>
				<div className="bg-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-400 space-y-1">
					<div>docker compose up -d</div>
					<div className="text-zinc-600"># Wait 30s for all services to start</div>
					<div className="mt-1"># Then configure each service:</div>
					<div className="text-zinc-500"># Radarr: http://localhost:7878</div>
					<div className="text-zinc-500"># Sonarr: http://localhost:8989</div>
					<div className="text-zinc-500"># Lidarr: http://localhost:8686</div>
					<div className="text-zinc-500"># Prowlarr: http://localhost:9696</div>
					<div className="text-zinc-500"># Readarr: http://localhost:8787</div>
					<div className="text-zinc-500"># Overseerr: http://localhost:5055</div>
					<div className="text-zinc-500"># Bazarr: http://localhost:6767</div>
					<div className="text-zinc-500"># Jellyfin: http://localhost:8096</div>
				</div>
			</section>

			{/* Service Installation Guide */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-3">
					<Server size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Per-Service Installation Guide</h3>
				</div>
				<p className="text-xs text-zinc-500 mb-3">
					Click any service to expand its installation instructions and API key location.
				</p>
				<div className="space-y-2">
					{serviceGuides.map((svc) => (
						<div key={svc.name} className="bg-zinc-800 rounded-lg overflow-hidden">
							<button
								type="button"
								onClick={() => setExpandedService(expandedService === svc.name ? null : svc.name)}
								className="w-full flex items-center justify-between p-3 text-sm hover:bg-zinc-700/50 transition-colors"
							>
								<div className="flex items-center gap-2">
									<span className="font-medium text-zinc-200">{svc.name}</span>
									<code className="text-xs text-zinc-500 font-mono">:{svc.port}</code>
								</div>
								<ArrowRight
									size={14}
									className={`text-zinc-500 transition-transform ${expandedService === svc.name ? "rotate-90" : ""}`}
								/>
							</button>
							{expandedService === svc.name && (
								<div className="px-3 pb-3 space-y-2 animate-slide-up">
									<p className="text-xs text-zinc-400">{svc.description}</p>
									<div>
										<span className="text-xs text-zinc-500">Installation:</span>
										<div className="bg-zinc-900 rounded-lg p-2 mt-1 text-xs font-mono text-zinc-400 space-y-1">
											{svc.installSteps.map((step, i) => (
												<div key={`step-${i}`}>{step}</div>
											))}
										</div>
									</div>
									<div className="flex items-center gap-2 text-xs">
										<Key size={12} className="text-yellow-500" />
										<span className="text-zinc-500">API Key location:</span>
										<code className="bg-zinc-900 px-1.5 py-0.5 rounded text-yellow-400">{svc.apiKeyPath}</code>
									</div>
								</div>
							)}
						</div>
					))}
				</div>
			</section>

			{/* API Key Retrieval Summary */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-3">
					<Key size={18} className="text-yellow-500" />
					<h3 className="font-semibold text-sm">How to Get API Keys</h3>
				</div>
				<p className="text-xs text-zinc-500 mb-2">
					Every *arr service uses an API key for authentication. Here's the universal method:
				</p>
				<ol className="text-xs text-zinc-400 space-y-1 list-decimal list-inside ml-1">
					<li>Open the service's web UI (e.g. http://localhost:7878 for Radarr)</li>
					<li>
						Go to <span className="text-zinc-300">Settings → General</span>
					</li>
					<li>
						Find the <span className="text-zinc-300">API Key</span> field
					</li>
					<li>
						Copy the key and paste it into your <code className="bg-zinc-800 px-1 py-0.5 rounded">.env</code> file
					</li>
					<li>
						Set <code className="bg-zinc-800 px-1 py-0.5 rounded">SERVICE_ENABLED=true</code> for each service you want
						to use
					</li>
				</ol>
			</section>

			{/* Tool Reference */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<button
					type="button"
					onClick={() => setShowToolRef(!showToolRef)}
					className="w-full flex items-center justify-between"
				>
					<div className="flex items-center gap-2">
						<Activity size={18} className="text-zinc-400" />
						<h3 className="font-semibold text-sm">MCP Tool Reference ({tools.length} tools)</h3>
					</div>
					<ArrowRight size={14} className={`text-zinc-500 transition-transform ${showToolRef ? "rotate-90" : ""}`} />
				</button>
				{showToolRef && (
					<div className="mt-3 space-y-2 animate-slide-up">
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
				)}
			</section>

			{/* Links */}
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
						<ExternalLink size={14} /> Servarr Wiki (official docs)
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
					<a
						href="https://prowlarr.com"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> Prowlarr
					</a>
					<a
						href="https://overseerr.dev"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> Overseerr
					</a>
				</div>
			</section>
		</div>
	);
}
