import { ServicePage } from "./ServicePages";
export default function SonarrPage() {
	return <ServicePage title="Sonarr" subtitle="TV Series" color="sonarr" endpoint="/api/sonarr/summary" />;
}
