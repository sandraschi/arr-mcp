import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import BazarrPage from "./pages/BazarrPage";
import ChatPage from "./pages/ChatPage";
import Dashboard from "./pages/Dashboard";
import HelpPage from "./pages/HelpPage";
import InboxPage from "./pages/InboxPage";
import InspectorPage from "./pages/InspectorPage";
import LidarrPage from "./pages/LidarrPage";
import LoggerPage from "./pages/LoggerPage";
import OrchestratePage from "./pages/OrchestratePage";
import OverseerrPage from "./pages/OverseerrPage";
import ProwlarrPage from "./pages/ProwlarrPage";
import RadarrPage from "./pages/RadarrPage";
import ReadarrPage from "./pages/ReadarrPage";
import SettingsPage from "./pages/SettingsPage";
import SkillsPage from "./pages/SkillsPage";
import SonarrPage from "./pages/SonarrPage";
import ToolsPage from "./pages/ToolsPage";

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
				<Route path="inbox" element={<InboxPage />} />
				<Route path="tools" element={<ToolsPage />} />
				<Route path="skills" element={<SkillsPage />} />
				<Route path="chat" element={<ChatPage />} />
				<Route path="inspector" element={<InspectorPage />} />
				<Route path="logger" element={<LoggerPage />} />
				<Route path="help" element={<HelpPage />} />
				<Route path="settings" element={<SettingsPage />} />
				<Route path="*" element={<Navigate to="/" replace />} />
			</Route>
		</Routes>
	);
}
