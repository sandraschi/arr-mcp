import { ArrowRight, Container, ExternalLink, Key } from "lucide-react";
import { Link } from "react-router-dom";

export interface ServiceSetup {
	label: string;
	subtitle: string;
	default_port: number;
	compose_service: string;
	image: string;
	env_keys: string[];
	key_location: string;
}

/**
 * Empty state for unconfigured services: install path + API key steps
 * instead of a raw HTTP 404. Driven by the backend `setup` payload.
 */
export default function SetupPanel({
	setup,
	serviceKey,
	containerRunning,
	containerPort,
}: {
	setup: ServiceSetup;
	serviceKey: string;
	containerRunning?: boolean;
	containerPort?: number | null;
}) {
	const port = containerPort ?? setup.default_port;
	const serviceUrl = `http://localhost:${port}`;

	return (
		<div
			className="bg-zinc-900 border border-dashed border-zinc-700 rounded-xl p-6 mb-4"
			data-testid={`setup-panel-${serviceKey}`}
		>
			<h3 className="font-semibold text-sm mb-1">{setup.label} is not connected</h3>
			<p className="text-xs text-zinc-500 mb-4">
				{setup.subtitle} — connect it once, then this page shows live library stats.
			</p>

			{containerRunning && (
				<div className="flex items-center gap-2 text-xs text-green-400 bg-green-950/40 border border-green-900/50 rounded-lg px-3 py-2 mb-4">
					<Container size={14} />
					<span>
						Detected a running {setup.label} container{port !== setup.default_port ? ` on :${port}` : ""} — you only
						need the API key below.
					</span>
				</div>
			)}

			<ol className="space-y-3 text-sm">
				<li className="flex gap-3">
					<span className="shrink-0 w-5 h-5 rounded-full bg-zinc-800 text-zinc-300 text-xs flex items-center justify-center font-mono">
						1
					</span>
					<div>
						<p className="text-zinc-200 text-xs font-medium mb-1">Start {setup.label}</p>
						<code className="block bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs font-mono text-zinc-300 overflow-x-auto">
							docker compose up -d {setup.compose_service}
						</code>
						<p className="text-xs text-zinc-600 mt-1">
							…or any install from the Help page (native installers work too).
						</p>
					</div>
				</li>
				<li className="flex gap-3">
					<span className="shrink-0 w-5 h-5 rounded-full bg-zinc-800 text-zinc-300 text-xs flex items-center justify-center font-mono">
						2
					</span>
					<div>
						<p className="text-zinc-200 text-xs font-medium mb-1">Copy its API key</p>
						<p className="text-xs text-zinc-500">
							Open <span className="text-zinc-300 font-mono">{serviceUrl}</span>, finish the first-run wizard if shown,
							then find the key at{" "}
							<code className="bg-zinc-800 px-1.5 py-0.5 rounded text-yellow-400">{setup.key_location}</code>
						</p>
					</div>
				</li>
				<li className="flex gap-3">
					<span className="shrink-0 w-5 h-5 rounded-full bg-zinc-800 text-zinc-300 text-xs flex items-center justify-center font-mono">
						3
					</span>
					<div>
						<p className="text-zinc-200 text-xs font-medium mb-1">Add to .env and restart the backend</p>
						<code className="block bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs font-mono text-zinc-300 overflow-x-auto whitespace-pre">
							{setup.env_keys
								.map((k) => `${k}=${k.endsWith("_URL") ? serviceUrl : k.endsWith("_ENABLED") ? "true" : "<paste-key>"}`)
								.join("\n")}
						</code>
					</div>
				</li>
			</ol>

			<div className="flex flex-wrap gap-2 mt-5">
				<a
					href={serviceUrl}
					target="_blank"
					rel="noopener noreferrer"
					className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-zinc-100 text-zinc-900 font-medium hover:bg-white transition-colors"
				>
					<ExternalLink size={12} /> Open {setup.label} <span className="font-mono">:{port}</span>
				</a>
				<Link
					to="/help"
					className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors"
				>
					<Key size={12} /> Install & key guide <ArrowRight size={12} />
				</Link>
			</div>
		</div>
	);
}
