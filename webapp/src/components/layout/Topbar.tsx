import { useConnection } from "../../store/connection";

export default function Topbar() {
	const { status } = useConnection();

	return (
		<header className="h-10 border-b border-zinc-800 bg-zinc-900/80 backdrop-blur flex items-center justify-between px-4 shrink-0">
			<span className="text-sm font-medium text-zinc-400">Dashboard</span>
			<div className="flex items-center gap-2">
				<div
					data-testid="connection-status"
					className={`w-2 h-2 rounded-full ${status === "connected" ? "bg-green-500" : status === "connecting" ? "bg-yellow-500 animate-pulse" : "bg-red-500"}`}
				/>
				<span data-testid="connection-label" className="text-xs text-zinc-500 capitalize">
					{status}
				</span>
			</div>
		</header>
	);
}
