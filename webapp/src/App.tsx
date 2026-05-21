import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import BazarrPage from "./pages/BazarrPage";
import ChatPage from "./pages/ChatPage";
import Dashboard from "./pages/Dashboard";
import HelpPage from "./pages/HelpPage";
import LidarrPage from "./pages/LidarrPage";
import LoggerPage from "./pages/LoggerPage";
import OrchestratePage from "./pages/OrchestratePage";
import OverseerrPage from "./pages/OverseerrPage";
import ProwlarrPage from "./pages/ProwlarrPage";
import RadarrPage from "./pages/RadarrPage";
import ReadarrPage from "./pages/ReadarrPage";
import SettingsPage from "./pages/SettingsPage";
import SonarrPage from "./pages/SonarrPage";

export default function App() {
	return (
		<Routes>
			<Route element={<AppLayout />}>
				<Route index element={<Dashboard />} />
				<Route path="radarr" element={<RadarrPage />} />
				<Route path="sonarr" element={<SonarrPage />} />
				<Route path="lidarr" element={<LidarrPage />} />
				<Route path="prowlarr" element={<ProwlarrPage />} />
				<Route path="readarr" element={<ReadarrPage />} />
				<Route path="overseerr" element={<OverseerrPage />} />
				<Route path="bazarr" element={<BazarrPage />} />
				<Route path="orchestrate" element={<OrchestratePage />} />
				<Route path="chat" element={<ChatPage />} />
				<Route path="logger" element={<LoggerPage />} />
				<Route path="help" element={<HelpPage />} />
				<Route path="settings" element={<SettingsPage />} />
				<Route path="*" element={<Navigate to="/" replace />} />
			</Route>
		</Routes>
	);
}
