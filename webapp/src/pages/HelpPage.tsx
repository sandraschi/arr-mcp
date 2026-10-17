import {
	Activity,
	ArrowRight,
	Book,
	Box,
	Check,
	Copy,
	ExternalLink,
	HelpCircle,
	Key,
	Network,
	Server,
	Terminal,
} from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { textColor } from "../utils/colors";

function CopyButton({ text }: { text: string }) {
	const [copied, setCopied] = useState(false);
	async function copy() {
		try {
			await navigator.clipboard.writeText(text);
		} catch {
			const ta = document.createElement("textarea");
			ta.value = text;
			document.body.appendChild(ta);
			ta.select();
			document.execCommand("copy");
			document.body.removeChild(ta);
		}
		setCopied(true);
		setTimeout(() => setCopied(false), 1500);
	}
	return (
		<button
			type="button"
			onClick={copy}
			title="Copy to clipboard"
			className="shrink-0 text-zinc-500 hover:text-zinc-200 transition-colors"
		>
			{copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
		</button>
	);
}

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
		operations: "list, lookup, get, add, search, delete, update",
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
		operations: "list, get, lookup, search, set_monitored",
		description: "Manage Readarr books — list by author, search, toggle monitoring.",
		color: "readarr",
	},
	{
		name: "readarr_add_book",
		operations: "add one book by exact foreign ID (existing or new author)",
		description: "Add exactly one book — duplicate-proof by foreign ID, dry-run safe.",
		color: "readarr",
	},
	{
		name: "readarr_delete_book",
		operations: "preview (dry_run) or delete one book, author retained",
		description: "Delete one book with preview-first safety; file deletes need confirmation.",
		color: "readarr",
	},
	{
		name: "readarr_delete_books",
		operations: "preflight + sequential bulk delete (≤100), authors retained",
		description: "Bulk delete with all-IDs-preflighted before the first mutation.",
		color: "readarr",
	},
	{
		name: "readarr_add_options",
		operations: "root folders, quality/metadata profiles, tags for adds",
		description: "Read-only discovery of the choices a new-author add needs.",
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
		operations: "request, status, check_jellyfin, check_plex, check_emby, queue",
		description: "Cross-arr orchestration — request media with library check + auto-routing.",
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
	route: string;
	description: string;
	does: string;
	apiKeyPath: string;
	installSteps: string[];
	afterInstall: string[];
	gotcha: string;
	tools: string[];
}

const serviceGuides: ServiceGuide[] = [
	{
		name: "Radarr",
		port: 7878,
		route: "/radarr",
		description:
			"Movie collection manager — finds movies, sends them to your download client, imports and renames them.",
		does: "Give it a movie and it handles search → download → import → rename, forever, for your whole library.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Compose (recommended): docker compose up -d radarr — or the Dashboard's Start button",
			"Standalone: docker run -d --name=radarr -p 7878:7878 -v /path/to/config:/config -v /path/to/movies:/movies lscr.io/linuxserver/radarr:latest",
			"Native installer: https://radarr.video",
		],
		afterInstall: [
			"Settings → Media Management: add a root folder (/movies on compose), turn on renaming so files land tidy.",
			"Settings → Download Clients: add qBittorrent or SABnzbd — without one, nothing ever downloads.",
			"Settings → Indexers: add via Prowlarr (recommended) so every *arr shares the same indexers.",
			"Back here: Settings → Services → Radarr → paste URL + key → Test → Save.",
		],
		gotcha:
			"“Added but never downloads” is always a missing download client or missing indexers — check System → Events first.",
		tools: ["radarr_movies"],
	},
	{
		name: "Sonarr",
		port: 8989,
		route: "/sonarr",
		description: "TV series manager — tracks episodes as they air and grabs them automatically.",
		does: "Follow a show once; it monitors future episodes, upgrades quality when better releases appear, and organizes seasons.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Compose (recommended): docker compose up -d sonarr — or the Dashboard's Start button",
			"Standalone: docker run -d --name=sonarr -p 8989:8989 -v /path/to/config:/config -v /path/to/tv:/tv lscr.io/linuxserver/sonarr:latest",
			"Native installer: https://sonarr.tv",
		],
		afterInstall: [
			"Settings → Media Management: root folder (/tv on compose).",
			"When adding a series choose monitoring wisely: Future (new episodes only) vs All (whole back-catalog).",
			"Connect a download client and Prowlarr indexers, same as Radarr.",
			"Back here: Settings → Services → Sonarr → paste URL + key → Test → Save.",
		],
		gotcha:
			"A monitored episode on an unmonitored series never grabs — enable the series first, then the episode flag.",
		tools: ["sonarr_series", "sonarr_episodes"],
	},
	{
		name: "Lidarr",
		port: 8686,
		route: "/lidarr",
		description: "Music manager — builds your library artist by artist from MusicBrainz metadata.",
		does: "Add an artist and it fetches their discography, matches metadata, and keeps tags and filenames consistent.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Compose (recommended): docker compose up -d lidarr — or the Dashboard's Start button",
			"Standalone: docker run -d --name=lidarr -p 8686:8686 -v /path/to/config:/config -v /path/to/music:/music lscr.io/linuxserver/lidarr:latest",
		],
		afterInstall: [
			"Settings → Media Management: root folder (/music), metadata profile (controls tags and naming).",
			"Add artists by MusicBrainz ID (via lookup), not by typed name — names mismatch constantly.",
			"Connect a download client and Prowlarr indexers.",
			"Back here: Settings → Services → Lidarr → paste URL + key → Test → Save.",
		],
		gotcha:
			"Compilations and Various Artists releases match poorly — per-album monitoring lets you tame the back-catalog.",
		tools: ["lidarr_artists", "lidarr_albums"],
	},
	{
		name: "Prowlarr",
		port: 9696,
		route: "/prowlarr",
		description: "Indexer backbone — configure Usenet/torrent indexers once, share them with every *arr.",
		does: "The single place indexers live. It pushes them out to Radarr/Sonarr/Lidarr/Readarr so you never configure the same indexer four times.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Compose (recommended): docker compose up -d prowlarr — or the Dashboard's Start button",
			"Standalone: docker run -d --name=prowlarr -p 9696:9696 -v /path/to/config:/config lscr.io/linuxserver/prowlarr:latest",
		],
		afterInstall: [
			"Indexers → Add your indexers (test each one — red means wrong credentials or URL).",
			"Settings → Apps → add Radarr/Sonarr/Lidarr/Readarr (each needs its own API key), then Sync.",
			'Whenever you edit indexers later: prowlarr_applications(operation="sync_all") — apps keep stale lists otherwise.',
			"Back here: Settings → Services → Prowlarr → paste URL + key → Test → Save.",
		],
		gotcha: "Indexer edits do nothing until synced to the apps — sync_all is the step everyone forgets.",
		tools: ["prowlarr_indexers", "prowlarr_search", "prowlarr_applications", "prowlarr_history"],
	},
	{
		name: "Readarr",
		port: 8787,
		route: "/readarr",
		description: "Book manager — ebooks and audiobooks, still pre-release upstream.",
		does: "Tracks authors and grabs their books. Youngest of the family: expect rough edges, but the core add/monitor flow works.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Compose (recommended): docker compose up -d readarr — or the Dashboard's Start button",
			"Standalone: docker run -d --name=readarr -p 8787:8787 -v /path/to/config:/config -v /path/to/books:/books lscr.io/linuxserver/readarr:amd64-develop-0.4.18.2805-ls157",
		],
		afterInstall: [
			"Settings → Media Management: root folder (/books). Metadata comes from Goodreads/Google Books.",
			"New-author adds need quality profile + metadata profile + root folder — readarr_add_options() lists the legal choices.",
			"Back here: Settings → Services → Readarr → paste URL + key → Test → Save.",
		],
		gotcha:
			"Upstream retired the floating :develop tag — the stack pins amd64-develop-0.4.18.2805-ls157. Don't “upgrade” it to :develop.",
		tools: ["readarr_authors", "readarr_books", "readarr_add_book", "readarr_delete_book", "readarr_add_options"],
	},
	{
		name: "Overseerr",
		port: 5055,
		route: "/overseerr",
		description: "Request portal — the family-friendly front door for “I want to watch…”",
		does: "Household members browse and request movies/shows; you approve or decline. Approved requests flow into Radarr/Sonarr.",
		apiKeyPath: "Settings → General → API Key (created by the setup wizard)",
		installSteps: [
			"Compose (recommended): docker compose up -d overseerr — or the Dashboard's Start button",
			"Standalone: docker run -d --name=overseerr -p 5055:5055 -v /path/to/config:/app/config sctx/overseerr:latest",
		],
		afterInstall: [
			"Open http://localhost:5055 and run the setup wizard: connect Radarr + Sonarr, then Plex/Jellyfin.",
			"The API key is generated during setup — Settings → General.",
			"Add users for each household member so requests carry identity.",
			"Back here: Settings → Services → Overseerr → paste URL + key → Test → Save.",
		],
		gotcha:
			"No key until the wizard runs. And request triage needs exact media IDs — overseerr_search first, never guess.",
		tools: ["overseerr_requests", "overseerr_search", "overseerr_users"],
	},
	{
		name: "Bazarr",
		port: 6767,
		route: "/bazarr",
		description: "Subtitle manager — keeps every movie and episode subtitled without thinking about it.",
		does: "Watches your Sonarr/Radarr libraries and downloads missing subtitles from your providers in your languages.",
		apiKeyPath: "Settings → General → API Key",
		installSteps: [
			"Compose (recommended): docker compose up -d bazarr — or the Dashboard's Start button",
			"Standalone: docker run -d --name=bazarr -p 6767:6767 -v /path/to/config:/config -v /path/to/movies:/movies -v /path/to/tv:/tv lscr.io/linuxserver/bazarr:latest",
		],
		afterInstall: [
			"Settings → Sonarr/Radarr: connect both (each needs its own API key — Bazarr reads their libraries).",
			"Settings → Providers: add at least one (OpenSubtitles needs an account) and enable your languages.",
			"Settings → Languages: enable the subtitle languages you actually watch.",
			"Back here: Settings → Services → Bazarr → paste URL + key → Test → Save.",
		],
		gotcha: "Empty search results mean no providers configured — not missing subtitles. Check providers first, always.",
		tools: ["bazarr_subtitles"],
	},
];

export default function HelpPage() {
	const [expandedService, setExpandedService] = useState<string | null>(null);
	const [showToolRef, setShowToolRef] = useState(false);

	return (
		<div className="animate-fade-in max-w-3xl" data-testid="help-page">
			<div className="flex items-center gap-3 mb-6">
				<HelpCircle size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Help</h2>
			</div>

			{/* What is arr-mcp */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4" data-testid="help-about">
				<div className="flex items-center gap-2 mb-3">
					<Book size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">What is arr-mcp?</h3>
				</div>
				<p className="text-sm text-zinc-400 leading-relaxed">
					arr-mcp is a FastMCP 3.4 server that puts the complete *arr automation stack under one roof: Radarr (Movies),
					Sonarr (TV), Lidarr (Music), Prowlarr (Indexers), Readarr (Books), Overseerr (Requests), and Bazarr
					(Subtitles). Each service is independently optional. Connect them in{" "}
					<Link to="/settings" className="text-zinc-200 underline">
						Settings → Services
					</Link>{" "}
					— paste URL + API key, Test, Save — no config files, no restart. (A{" "}
					<code className="bg-zinc-800 px-1.5 py-0.5 rounded text-xs">.env</code> fallback exists for container setups.)
				</p>
			</section>

			{/* Quick Start */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4" data-testid="help-quickstart">
				<div className="flex items-center gap-2 mb-3">
					<Terminal size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Quick Start — no terminal required</h3>
				</div>
				<ol className="text-sm text-zinc-400 space-y-2 list-decimal list-inside ml-1 leading-relaxed">
					<li>
						<span className="text-zinc-200">Start the stack:</span> on the{" "}
						<Link to="/" className="text-zinc-200 underline">
							Dashboard
						</Link>{" "}
						press <span className="text-zinc-200">Start all missing</span> (or the Start button on any service page).
						Containers pull and start by themselves.
					</li>
					<li>
						<span className="text-zinc-200">Connect each service:</span>{" "}
						<Link to="/settings" className="text-zinc-200 underline">
							Settings → Services
						</Link>{" "}
						— paste its URL + API key (locations below), Test, Save. Cards turn green immediately.
					</li>
					<li>
						<span className="text-zinc-200">Request something:</span> the{" "}
						<Link to="/orchestrate" className="text-zinc-200 underline">
							Orchestrate
						</Link>{" "}
						page runs the whole pipeline (library check → type detection → add).
					</li>
				</ol>
				<p className="text-xs text-zinc-600 mt-3">
					Prefer the terminal? Clone, <span className="font-mono">uv sync</span>,{" "}
					<span className="font-mono">uv run arr-mcp --http</span>, webapp{" "}
					<span className="font-mono">npm run dev</span> — same result, more typing.
				</p>
			</section>

			{/* Docker Compose */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4">
				<div className="flex items-center gap-2 mb-3">
					<Box size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Docker Compose — Full *Arr Stack</h3>
				</div>
				<p className="text-sm text-zinc-400 mb-3">
					The repo includes a <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-xs">docker-compose.yml</code> with
					the 7 *arr services plus Jellyfin and the arr-mcp backend (the webapp itself needs{" "}
					<span className="font-mono">--profile webapp</span>). From the repo root,{" "}
					<span className="font-mono">docker compose up -d</span> starts the stack; first pulls take a while and
					registries throttle parallel pulls, so prefer the Dashboard's{" "}
					<span className="text-zinc-200">Start all missing</span> button, which pulls sequentially.
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
					Click a service for the full picture: what it does, how to install it, the three things that make it actually
					work, where its API key lives, and the gotcha that bites everyone once. Compose commands run from the repo
					root — or skip the terminal with the Dashboard's Start buttons.
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
								<div className="px-3 pb-3 space-y-3 animate-slide-up">
									<p className="text-xs text-zinc-300 leading-relaxed">{svc.does}</p>
									<div>
										<span className="text-xs text-zinc-500">Install:</span>
										<div className="bg-zinc-900 rounded-lg p-2 mt-1 text-xs font-mono text-zinc-400 space-y-1.5">
											{svc.installSteps.map((step, i) => (
												<div key={`step-${i}`} className="flex items-start justify-between gap-2">
													<span>{step}</span>
													<CopyButton text={step} />
												</div>
											))}
										</div>
									</div>
									<div>
										<span className="text-xs text-zinc-500">Make it actually work:</span>
										<ol className="mt-1 space-y-1 text-xs text-zinc-400 list-decimal list-inside ml-1">
											{svc.afterInstall.map((step, i) => (
												<li key={`after-${i}`}>{step}</li>
											))}
										</ol>
									</div>
									<div className="flex items-start gap-2 text-xs bg-yellow-950/30 border border-yellow-900/40 rounded-lg p-2">
										<span className="text-yellow-500 font-medium shrink-0">Gotcha:</span>
										<span className="text-zinc-400">{svc.gotcha}</span>
									</div>
									<div className="flex items-center gap-2 text-xs">
										<Key size={12} className="text-yellow-500" />
										<span className="text-zinc-500">API key:</span>
										<code className="bg-zinc-900 px-1.5 py-0.5 rounded text-yellow-400">{svc.apiKeyPath}</code>
									</div>
									<div className="flex flex-wrap items-center gap-2 text-xs">
										<Link
											to={svc.route}
											className="inline-flex items-center gap-1 text-zinc-300 hover:text-white bg-zinc-900 px-2 py-1 rounded transition-colors"
										>
											Open {svc.name} page <ArrowRight size={12} />
										</Link>
										<Link
											to="/settings"
											className="inline-flex items-center gap-1 text-zinc-400 hover:text-zinc-200 transition-colors"
										>
											Connect in Settings
										</Link>
										<span className="text-zinc-600 font-mono">tools: {svc.tools.join(", ")}</span>
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
					Every *arr service uses an API key. The normal path needs no files:
				</p>
				<ol className="text-xs text-zinc-400 space-y-1 list-decimal list-inside ml-1">
					<li>Open the service's web UI (e.g. http://localhost:7878 for Radarr)</li>
					<li>
						Go to <span className="text-zinc-300">Settings → General</span>, find the{" "}
						<span className="text-zinc-300">API Key</span> field
					</li>
					<li>
						Paste it into{" "}
						<Link to="/settings" className="text-zinc-200 underline">
							Settings → Services
						</Link>{" "}
						next to the service, Test, Save — live immediately
					</li>
				</ol>
				<p className="text-xs text-zinc-600 mt-2">
					Keys are stored in <span className="font-mono">config/arr-services.json</span> (gitignored) and never shown
					back. The legacy path — <span className="font-mono">SERVICE_URL</span>/
					<span className="font-mono">SERVICE_API_KEY</span>/<span className="font-mono">SERVICE_ENABLED</span> in{" "}
					<span className="font-mono">.env</span> — still works.
				</p>
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
									<code className={`text-xs font-mono px-1.5 py-0.5 rounded bg-zinc-700 ${textColor(tool.color)}`}>
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

			{/* Fleet topology: who owns what */}
			<section className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 mb-4" data-testid="help-fleet">
				<div className="flex items-center gap-2 mb-3">
					<Network size={18} className="text-zinc-400" />
					<h3 className="font-semibold text-sm">Fleet topology — arr-mcp, plex-mcp, jellyfin-mcp</h3>
				</div>
				<p className="text-sm text-zinc-400 leading-relaxed mb-3">
					Three servers, three jobs. <span className="text-zinc-200">arr-mcp acquires media</span> (Radarr, Sonarr,
					Lidarr, Prowlarr, Readarr, Overseerr, Bazarr).{" "}
					<span className="text-zinc-200">plex-mcp owns the Plex server connection</span> (library, playback, RAG), and{" "}
					<span className="text-zinc-200">jellyfin-mcp owns Jellyfin</span>. arr-mcp talks to your Plex/Jellyfin/Emby{" "}
					<em>servers</em> directly for before-you-download availability checks — it does not route through the sibling
					MCP servers, and there is intentionally no shared state between them. The fleet lane is: request in arr-mcp
					(or Overseerr) → download via *arr → watch in Plex/Jellyfin. The Dashboard probes both siblings live and links
					to their dashboards when they are running.
				</p>
				<div className="text-xs font-mono text-zinc-500 space-y-1">
					<div>plex-mcp backend :10740 · frontend :10741</div>
					<div>jellyfin-mcp backend :10934 · frontend :10935</div>
				</div>
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
					<a
						href="https://lidarr.audio"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> Lidarr
					</a>
					<a
						href="https://readarr.com"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> Readarr
					</a>
					<a
						href="https://www.bazarr.media"
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors"
					>
						<ExternalLink size={14} /> Bazarr
					</a>
				</div>
			</section>
		</div>
	);
}
