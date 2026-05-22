import {
	BookOpen,
	Film,
	HelpCircle,
	LayoutDashboard,
	MessageSquare,
	Music,
	Puzzle,
	ScrollText,
	Search,
	Settings,
	Subtitles,
	Tv,
	UserCheck,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { APP_VERSION } from "../../version";

const navItems = [
	{ to: "/", icon: LayoutDashboard, label: "Dashboard" },
	{ to: "/radarr", icon: Film, label: "Radarr", color: "radarr" },
	{ to: "/sonarr", icon: Tv, label: "Sonarr", color: "sonarr" },
	{ to: "/lidarr", icon: Music, label: "Lidarr", color: "lidarr" },
	{ to: "/prowlarr", icon: Search, label: "Prowlarr", color: "prowlarr" },
	{ to: "/readarr", icon: BookOpen, label: "Readarr", color: "readarr" },
	{ to: "/overseerr", icon: UserCheck, label: "Overseerr", color: "overseerr" },
	{ to: "/bazarr", icon: Subtitles, label: "Bazarr", color: "bazarr" },
	{ to: "/orchestrate", icon: Puzzle, label: "Orchestrate" },
];

const bottomItems = [
	{ to: "/chat", icon: MessageSquare, label: "Chat" },
	{ to: "/logger", icon: ScrollText, label: "Logger" },
	{ to: "/help", icon: HelpCircle, label: "Help" },
	{ to: "/settings", icon: Settings, label: "Settings" },
];

const colorMap: Record<string, { bg: string; text: string; border: string }> = {
	radarr: { bg: "bg-radarr/10", text: "text-radarr", border: "border-l-radarr" },
	sonarr: { bg: "bg-sonarr/10", text: "text-sonarr", border: "border-l-sonarr" },
	lidarr: { bg: "bg-lidarr/10", text: "text-lidarr", border: "border-l-lidarr" },
	prowlarr: { bg: "bg-prowlarr/10", text: "text-prowlarr", border: "border-l-prowlarr" },
	readarr: { bg: "bg-readarr/10", text: "text-readarr", border: "border-l-readarr" },
	overseerr: { bg: "bg-overseerr/10", text: "text-overseerr", border: "border-l-overseerr" },
	bazarr: { bg: "bg-bazarr/10", text: "text-bazarr", border: "border-l-bazarr" },
};

export default function Sidebar() {
	return (
		<aside className="w-56 bg-zinc-900 border-r border-zinc-800 flex flex-col shrink-0">
			<div className="p-4 border-b border-zinc-800">
				<h1 className="text-lg font-bold tracking-tight">
					<span className="text-zinc-400">arr</span>
					<span className="text-zinc-100">-mcp</span>
				</h1>
				<p className="text-xs text-zinc-500 mt-0.5">*arr automation stack</p>
			</div>
			<nav className="flex-1 py-2 overflow-y-auto">
				{navItems.map((item) => {
					const colors = item.color ? colorMap[item.color] : null;
					return (
						<NavLink
							key={item.to}
							to={item.to}
							end={item.to === "/"}
							className={({ isActive }) =>
								`flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg text-sm transition-colors border-l-2 ${
									isActive
										? `${colors?.bg || "bg-zinc-800"} ${colors?.text || "text-zinc-100"} ${colors?.border || "border-l-zinc-400"} font-medium`
										: "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50 border-l-transparent"
								}`
							}
						>
							<item.icon size={18} />
							<span>{item.label}</span>
						</NavLink>
					);
				})}

				<div className="mx-3 my-2 border-t border-zinc-800" />

				{bottomItems.map((item) => (
					<NavLink
						key={item.to}
						to={item.to}
						className={({ isActive }) =>
							`flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg text-sm transition-colors ${
								isActive
									? "bg-zinc-800 text-zinc-100 font-medium"
									: "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
							}`
						}
					>
						<item.icon size={18} />
						<span>{item.label}</span>
					</NavLink>
				))}
			</nav>
			<div className="p-4 border-t border-zinc-800 text-xs text-zinc-600">arr-mcp v{APP_VERSION}</div>
		</aside>
	);
}
