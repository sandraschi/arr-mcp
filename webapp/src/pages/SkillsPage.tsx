import { BookMarked, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { mcpRequest } from "../utils/mcp";

interface SkillResource {
	uri: string;
	name: string;
	description: string;
}

export default function SkillsPage() {
	const [resources, setResources] = useState<SkillResource[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [search, setSearch] = useState("");
	const [selected, setSelected] = useState<string | null>(null);
	const [content, setContent] = useState("");
	const [contentLoading, setContentLoading] = useState(false);

	useEffect(() => {
		let mounted = true;
		async function load() {
			try {
				const result = await mcpRequest("resources/list", {});
				const list: Array<{ uri: string; name?: string; description?: string }> = result?.resources ?? [];
				if (mounted) {
					setResources(
						list.map((r) => ({
							uri: r.uri,
							name: r.name ?? r.uri,
							description: r.description ?? "",
						})),
					);
				}
			} catch (e) {
				if (mounted) setError(`Could not list server resources (${String(e)}).`);
			} finally {
				if (mounted) setLoading(false);
			}
		}
		load();
		return () => {
			mounted = false;
		};
	}, []);

	async function openResource(uri: string) {
		if (selected === uri) {
			setSelected(null);
			return;
		}
		setSelected(uri);
		setContent("");
		setContentLoading(true);
		try {
			const result = await mcpRequest("resources/read", { uri });
			const blocks: Array<{ text?: string }> = result?.contents ?? [];
			setContent(blocks.map((b) => b.text ?? "").join("\n"));
		} catch (e) {
			setContent(`Failed to read resource: ${String(e)}`);
		} finally {
			setContentLoading(false);
		}
	}

	const filtered = useMemo(() => {
		const q = search.trim().toLowerCase();
		if (!q) return resources;
		return resources.filter((r) => `${r.name} ${r.uri} ${r.description}`.toLowerCase().includes(q));
	}, [resources, search]);

	if (loading) {
		return (
			<div className="animate-fade-in">
				<h2 className="text-2xl font-bold mb-6">Skills</h2>
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
					<div className="h-4 bg-zinc-800 rounded w-40" />
				</div>
			</div>
		);
	}

	return (
		<div className="animate-fade-in">
			<div className="flex items-center gap-3 mb-1">
				<BookMarked size={24} className="text-zinc-300" />
				<h2 className="text-2xl font-bold">Skills</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded" data-testid="skills-count">
					{filtered.length} of {resources.length}
				</span>
			</div>
			<p className="text-sm text-zinc-500 mb-4">
				Server resources (<code className="text-zinc-400">resources/list</code>) - the same content MCP clients inject
				into model context. Select one to read it.
			</p>
			{error && <p className="text-xs text-amber-400 mb-3">{error}</p>}

			<div className="relative mb-4">
				<Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
				<input
					data-testid="skills-search"
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					placeholder="Search skills..."
					className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-9 pr-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
				/>
			</div>

			{filtered.length === 0 ? (
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center text-sm text-zinc-500">
					{resources.length === 0 ? "No skills exposed by the server yet." : "No skills match this search."}
				</div>
			) : (
				<div className="grid grid-cols-1 lg:grid-cols-3 gap-3" data-testid="skills-list">
					<div className="space-y-2">
						{filtered.map((r) => (
							<button
								type="button"
								key={r.uri}
								onClick={() => openResource(r.uri)}
								className={`w-full text-left bg-zinc-900 border rounded-xl p-3 transition-colors text-sm ${
									selected === r.uri ? "border-zinc-500" : "border-zinc-800 hover:border-zinc-600"
								}`}
							>
								<code className="text-xs text-zinc-200">{r.name}</code>
								<p className="text-xs text-zinc-500 mt-1 truncate">{r.uri}</p>
								{r.description && <p className="text-xs text-zinc-400 mt-1">{r.description}</p>}
							</button>
						))}
					</div>
					<div className="lg:col-span-2">
						{selected == null ? (
							<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center text-sm text-zinc-600 h-full">
								Select a skill to read its content.
							</div>
						) : contentLoading ? (
							<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 animate-pulse">
								<div className="h-4 bg-zinc-800 rounded w-2/3 mb-2" />
								<div className="h-4 bg-zinc-800 rounded w-1/2" />
							</div>
						) : (
							<pre className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 text-xs text-zinc-300 whitespace-pre-wrap overflow-y-auto max-h-[60vh] font-mono">
								{content || "(empty)"}
							</pre>
						)}
					</div>
				</div>
			)}
		</div>
	);
}
