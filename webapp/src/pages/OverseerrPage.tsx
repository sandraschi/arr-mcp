import { ServicePage } from "./ServicePages";
export default function OverseerrPage() {
	return (
		<ServicePage
			title="Overseerr"
			subtitle="Requests & Discovery"
			color="overseerr"
			endpoint="/api/overseerr/summary"
		/>
	);
}
