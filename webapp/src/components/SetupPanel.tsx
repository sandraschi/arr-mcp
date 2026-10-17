import { ArrowRight, Container, ExternalLink, Key, Loader2, Play } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../utils/api";

export interface ServiceSetup {
	label: string;
	subtitle: string;
	default_port: number;
	compose_service: string;
	compose_file?: string;
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
	const [starting, setStarting] = useState(false);
	const [startError, setStartError] = useState("");
	const [startOutput, setStartOutput] = useState("");
	const [started, setStarted] = useState(false);

	async function startContainer() {
		if (starting) return;
		setStarting(true);
		setStartError("");
		setStartOutput("");
		try {
			const result = await apiFetch<{ success: boolean; message: string; output: string }>("/api/docker/start", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ service: serviceKey }),
				timeoutMs: 200000,
			});
			if (result.success) {
				setStarted(true);
				setStartOutput(result.output);
			} else {
				setStartError(result.message + (result.output ? `\n${result.output}` : ""));
			}
		} catch (err) {
			setStartError(String(err));
		} finally {
			setStarting(false);
		}
	}

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
						<code className="block bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs font-mono text-zinc-300 overflow-x-auto whitespace-pre">
							{setup.compose_file
								? `docker compose -f ${setup.compose_file} up -d ${setup.compose_service}`
								: `docker compose up -d ${setup.compose_service}`}
						</code>
						<p className="text-xs text-zinc-600 mt-1">
							{setup.compose_file
								? "The -f flag makes it work from any directory (bare compose needs the YAML in front of you)."
								: "Run from the repo root, where docker-compose.yml lives — or use -f <path-to-yml>."}
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
				{setup.compose_file && !started && (
					<button
						type="button"
						onClick={startContainer}
						disabled={starting}
						className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-green-700 hover:bg-green-600 text-white font-medium disabled:opacity-50 transition-colors"
						data-testid={`start-container-${serviceKey}`}
					>
						{starting ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
						{starting ? "Starting… (first pull takes minutes)" : `Start ${setup.label} now`}
					</button>
				)}
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
			{started && (
				<p className="text-xs text-green-400 mt-3" data-testid={`started-ok-${serviceKey}`}>
					Container started — open {setup.label} below, finish the first-run wizard if shown, then continue with step 2
					(API key).
				</p>
			)}
			{startOutput && (
				<pre className="text-xs font-mono text-zinc-500 bg-zinc-950 border border-zinc-800 rounded-lg p-3 mt-3 overflow-x-auto whitespace-pre-wrap">
					{startOutput}
				</pre>
			)}
			{startError && (
				<p className="text-xs text-red-400 mt-3 whitespace-pre-wrap" data-testid={`start-error-${serviceKey}`}>
					{startError}
				</p>
			)}
		</div>
	);
}
