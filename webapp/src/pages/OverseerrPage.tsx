import { CheckCircle, Clock, Inbox, Search, UserCheck, Users, XCircle } from "lucide-react";

export default function OverseerrPage() {
	return (
		<div className="animate-fade-in">
			<div className="flex items-center gap-3 mb-6">
				<UserCheck size={24} className="text-overseerr" />
				<h2 className="text-2xl font-bold">Overseerr</h2>
				<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Media Requests & Discovery</span>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				<QuickAction icon={Inbox} label="Requests" desc="View all requests" color="overseerr" />
				<QuickAction icon={Search} label="Search" desc="Search TMDB for media" color="overseerr" />
				<QuickAction icon={CheckCircle} label="Approve" desc="Approve pending requests" color="overseerr" />
				<QuickAction icon={XCircle} label="Decline" desc="Decline requests" color="overseerr" />
				<QuickAction icon={Users} label="Users" desc="Manage users & permissions" color="overseerr" />
				<QuickAction icon={Clock} label="Pending" desc="View pending requests" color="overseerr" />
			</div>

			<div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
				<h3 className="font-semibold mb-3 text-sm text-zinc-300">MCP Tools</h3>
				<div className="space-y-2 text-sm">
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-overseerr">overseerr_requests</code>
						<span className="text-zinc-500">— list, get, create, approve, decline, delete, count, pending</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-overseerr">overseerr_search</code>
						<span className="text-zinc-500">— search TMDB for movies, TV shows, people</span>
					</div>
					<div className="flex items-center gap-2 text-zinc-400">
						<code className="bg-zinc-800 px-2 py-0.5 rounded text-xs text-overseerr">overseerr_users</code>
						<span className="text-zinc-500">— list users, get user, view user requests</span>
					</div>
				</div>
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
	icon: typeof UserCheck;
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
