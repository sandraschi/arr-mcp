import { useEffect } from "react";
import { Outlet } from "react-router-dom";
import { useConnection } from "../../store/connection";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function AppLayout() {
	const { check, setStatus } = useConnection();

	useEffect(() => {
		check();
		const interval = setInterval(check, 10000);
		return () => clearInterval(interval);
	}, [check]);

	useEffect(() => {
		let unlisten: (() => void) | undefined;
		(async () => {
			try {
				const { listen } = await import("@tauri-apps/api/event");
				unlisten = await listen<string>("backend-status", (event) => {
					if (event.payload === "ready") check();
					else if (typeof event.payload === "string" && event.payload.startsWith("error:")) setStatus("offline");
				});
			} catch {
				/* not in Tauri */
			}
		})();
		return () => {
			if (unlisten) unlisten();
		};
	}, [check, setStatus]);

	return (
		<div className="flex h-screen overflow-hidden">
			<Sidebar />
			<div className="flex-1 flex flex-col overflow-hidden">
				<Topbar />
				<main className="flex-1 overflow-y-auto p-6">
					<Outlet />
				</main>
			</div>
		</div>
	);
}
