/**
 * Static Tailwind class maps per service color key.
 *
 * Tailwind scans source for literal class names, so dynamic `text-${color}`
 * interpolations NEVER generate CSS. Every class here is a full literal —
 * always look up through these maps instead of interpolating.
 */
export const COLOR_TEXT: Record<string, string> = {
	radarr: "text-radarr",
	sonarr: "text-sonarr",
	lidarr: "text-lidarr",
	prowlarr: "text-prowlarr",
	readarr: "text-readarr",
	overseerr: "text-overseerr",
	bazarr: "text-bazarr",
	zinc: "text-zinc-300",
};

export const COLOR_BG: Record<string, string> = {
	radarr: "bg-radarr",
	sonarr: "bg-sonarr",
	lidarr: "bg-lidarr",
	prowlarr: "bg-prowlarr",
	readarr: "bg-readarr",
	overseerr: "bg-overseerr",
	bazarr: "bg-bazarr",
	zinc: "bg-zinc-500",
};

export const COLOR_BORDER_SOFT: Record<string, string> = {
	radarr: "border-radarr/30",
	sonarr: "border-sonarr/30",
	lidarr: "border-lidarr/30",
	prowlarr: "border-prowlarr/30",
	readarr: "border-readarr/30",
	overseerr: "border-overseerr/30",
	bazarr: "border-bazarr/30",
	zinc: "border-zinc-700",
};

export function textColor(color: string): string {
	return COLOR_TEXT[color] ?? COLOR_TEXT.zinc;
}

export function bgColor(color: string): string {
	return COLOR_BG[color] ?? COLOR_BG.zinc;
}

export function borderSoft(color: string): string {
	return COLOR_BORDER_SOFT[color] ?? COLOR_BORDER_SOFT.zinc;
}
