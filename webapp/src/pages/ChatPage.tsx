import { Bot, Loader2, Send, Settings, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import {
	type LLMConfig,
	type LMStudioModel,
	type OllamaModel,
	chatWithLLM,
	fetchLMStudioModels,
	fetchOllamaModels,
	loadLLMConfig,
	saveLLMConfig,
} from "../utils/llm";

interface Message {
	role: "user" | "assistant" | "system";
	content: string;
}

export default function ChatPage() {
	const [config, setConfig] = useState<LLMConfig>(loadLLMConfig);
	const [messages, setMessages] = useState<Message[]>([]);
	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const [models, setModels] = useState<(OllamaModel | LMStudioModel)[]>([]);
	const [showSettings, setShowSettings] = useState(!config.selectedModel);
	const [loadingModels, setLoadingModels] = useState(false);
	const chatEndRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages]);

	useEffect(() => {
		if (config.provider !== "none") {
			loadModels(config);
		}
	}, [config.provider, config.ollamaUrl, config.lmstudioUrl]);

	async function loadModels(cfg: LLMConfig) {
		setLoadingModels(true);
		try {
			if (cfg.provider === "ollama") {
				const m = await fetchOllamaModels(cfg.ollamaUrl);
				setModels(m);
			} else if (cfg.provider === "lmstudio") {
				const m = await fetchLMStudioModels(cfg.lmstudioUrl);
				setModels(m);
			}
		} catch {
			setModels([]);
		} finally {
			setLoadingModels(false);
		}
	}

	async function sendMessage() {
		if (!input.trim() || loading) return;
		const userMsg: Message = { role: "user", content: input };
		setMessages((prev) => [...prev, userMsg]);
		setInput("");
		setLoading(true);
		try {
			const reply = await chatWithLLM(config, [...messages, userMsg]);
			setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
		} catch {
			setMessages((prev) => [
				...prev,
				{ role: "assistant", content: "Error: LLM request failed. Check your connection and model selection." },
			]);
		} finally {
			setLoading(false);
		}
	}

	function handleKeyDown(e: React.KeyboardEvent) {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	}

	return (
		<div className="animate-fade-in flex flex-col h-[calc(100vh-6rem)]">
			<div className="flex items-center justify-between mb-4">
				<div className="flex items-center gap-3">
					<Bot size={24} className="text-zinc-300" />
					<h2 className="text-2xl font-bold">Chat</h2>
					<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">
						{config.provider === "none" ? "No LLM" : config.provider === "ollama" ? "Ollama" : "LM Studio"}
					</span>
				</div>
				<button
					type="button"
					onClick={() => setShowSettings(!showSettings)}
					className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-sm text-zinc-300 transition-colors"
				>
					<Settings size={14} />
					<span>Settings</span>
				</button>
			</div>

			{showSettings && (
				<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 mb-4 animate-slide-up">
					<h3 className="font-semibold text-sm mb-3">LLM Configuration</h3>
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label className="text-xs text-zinc-500 block mb-1">Provider</label>
							<select
								value={config.provider}
								onChange={(e) => {
									const next = { ...config, provider: e.target.value as LLMConfig["provider"] };
									setConfig(next);
									saveLLMConfig(next);
								}}
								className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-zinc-500"
							>
								<option value="none">None (disabled)</option>
								<option value="ollama">Ollama</option>
								<option value="lmstudio">LM Studio</option>
							</select>
						</div>
						{config.provider === "ollama" && (
							<div>
								<label className="text-xs text-zinc-500 block mb-1">Ollama URL</label>
								<input
									type="text"
									value={config.ollamaUrl}
									onChange={(e) => {
										const next = { ...config, ollamaUrl: e.target.value };
										setConfig(next);
										saveLLMConfig(next);
									}}
									className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-zinc-500 font-mono"
								/>
							</div>
						)}
						{config.provider === "lmstudio" && (
							<div>
								<label className="text-xs text-zinc-500 block mb-1">LM Studio URL</label>
								<input
									type="text"
									value={config.lmstudioUrl}
									onChange={(e) => {
										const next = { ...config, lmstudioUrl: e.target.value };
										setConfig(next);
										saveLLMConfig(next);
									}}
									className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-zinc-500 font-mono"
								/>
							</div>
						)}
					</div>
					{config.provider !== "none" && (
						<div className="mt-3">
							<div className="flex items-center justify-between mb-1">
								<label className="text-xs text-zinc-500">Model</label>
								<button
									type="button"
									onClick={() => loadModels(config)}
									className="text-xs text-zinc-500 hover:text-zinc-300"
								>
									Refresh
								</button>
							</div>
							{loadingModels ? (
								<div className="text-xs text-zinc-500 flex items-center gap-2">
									<Loader2 size={12} className="animate-spin" /> Loading models...
								</div>
							) : (
								<select
									value={config.selectedModel}
									onChange={(e) => {
										const next = { ...config, selectedModel: e.target.value };
										setConfig(next);
										saveLLMConfig(next);
									}}
									className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-zinc-500"
								>
									<option value="">Select a model...</option>
									{config.provider === "ollama"
										? (models as OllamaModel[]).map((m) => (
												<option key={m.name} value={m.name}>
													{m.name}
												</option>
											))
										: (models as LMStudioModel[]).map((m) => (
												<option key={m.id} value={m.id}>
													{m.id}
												</option>
											))}
								</select>
							)}
						</div>
					)}
				</div>
			)}

			<div className="flex-1 overflow-y-auto bg-zinc-900 border border-zinc-800 rounded-xl p-4 mb-4">
				{messages.length === 0 && (
					<div className="text-center text-zinc-500 mt-20">
						<Bot size={48} className="mx-auto mb-3 text-zinc-700" />
						<p className="text-lg font-medium">arr-mcp Chat</p>
						<p className="text-sm mt-1">
							{config.provider === "none"
								? "Configure Ollama or LM Studio in Settings to start chatting."
								: `Connected to ${config.provider === "ollama" ? "Ollama" : "LM Studio"} — select a model to begin.`}
						</p>
					</div>
				)}
				{messages.map((msg, i) => (
					<div key={`msg-${i}`} className={`flex gap-3 mb-4 ${msg.role === "user" ? "justify-end" : ""}`}>
						{msg.role === "assistant" && (
							<div className="shrink-0 w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center">
								<Bot size={16} />
							</div>
						)}
						<div
							className={`max-w-[70%] rounded-xl px-4 py-2.5 text-sm ${
								msg.role === "user" ? "bg-zinc-700 text-zinc-100" : "bg-zinc-800 text-zinc-300"
							}`}
						>
							<pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
						</div>
						{msg.role === "user" && (
							<div className="shrink-0 w-8 h-8 rounded-full bg-zinc-600 flex items-center justify-center">
								<User size={16} />
							</div>
						)}
					</div>
				))}
				{loading && (
					<div className="flex gap-3 mb-4">
						<div className="shrink-0 w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center">
							<Bot size={16} />
						</div>
						<div className="bg-zinc-800 rounded-xl px-4 py-2.5">
							<Loader2 size={16} className="animate-spin text-zinc-400" />
						</div>
					</div>
				)}
				<div ref={chatEndRef} />
			</div>

			<div className="flex gap-2">
				<textarea
					value={input}
					onChange={(e) => setInput(e.target.value)}
					onKeyDown={handleKeyDown}
					placeholder={
						config.provider === "none" ? "Configure an LLM in Settings first..." : "Ask about your *arr stack..."
					}
					rows={2}
					className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:border-zinc-600 placeholder:text-zinc-600"
					disabled={config.provider === "none" || !config.selectedModel}
				/>
				<button
					type="button"
					onClick={sendMessage}
					disabled={loading || !input.trim() || config.provider === "none" || !config.selectedModel}
					className="px-4 py-2.5 bg-zinc-700 hover:bg-zinc-600 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl transition-colors self-end"
				>
					<Send size={16} />
				</button>
			</div>
		</div>
	);
}
