import { ServicePage } from "./ServicePages";
export default function ReadarrPage() {
	return <ServicePage title="Readarr" subtitle="Books" color="readarr" endpoint="/api/readarr/summary" />;
}
