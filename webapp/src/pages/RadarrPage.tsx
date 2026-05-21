import { ServicePage } from "./ServicePages";
export default function RadarrPage() {
	return <ServicePage title="Radarr" subtitle="Movies" color="radarr" endpoint="/api/radarr/summary" />;
}
