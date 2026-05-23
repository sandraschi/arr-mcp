"""Prefab-UI card builders for arr-mcp using prefab_ui components.

Matches fleet pattern from jellyfin-mcp and plex-mcp.
"""

from prefab_ui.components import Badge, Card, Metric, Row


def build_health_card(health_data: dict[str, dict]) -> Card:
    """Build a health status card for the entire *arr stack."""
    services = health_data.get("data", {})
    reachable = sum(1 for v in services.values() if v.get("reachable"))
    total = len(services)

    rows = []
    for name, info in services.items():
        status = "Online" if info.get("reachable") else "Offline"
        version = info.get("version", "—") or "—"
        rows.append(
            Row(
                children=[
                    Metric(label="Service", value=name.title()),
                    Metric(label="Status", value=status),
                    Metric(label="Version", value=str(version)),
                ]
            )
        )

    badges = [Badge(label=f"{reachable}/{total} Online")]
    if reachable == total:
        badges.append(Badge(label="All Systems Go"))

    return Card(children=rows, title="*arr Stack Health", badges=badges)


def build_calendar_card(calendar_data: dict[str, dict]) -> Card:
    """Build a calendar overview card."""
    data = calendar_data.get("data", {})
    rows = []
    for service, items in data.items():
        if not items:
            continue
        for item in items[:3]:
            title_str = (
                item.get("title")
                or (item.get("series") or {}).get("title", "")
                or (item.get("artist") or {}).get("artistName", "")
                or (item.get("author") or {}).get("authorName", "")
                or str(item)
            )
            date = item.get("inCinemas") or item.get("airDate") or item.get("releaseDate") or "—"
            rows.append(
                Row(
                    children=[
                        Metric(label="Date", value=str(date)),
                        Metric(label="From", value=service.title()),
                        Metric(label="Title", value=str(title_str)[:60]),
                    ]
                )
            )

    total = sum(len(v) for v in data.values())
    return Card(
        children=rows[:15],
        title="Upcoming Releases",
        badges=[Badge(label=f"{total} items")],
    )


def build_orchestrate_card(result: dict) -> Card:
    """Build a card showing orchestration pipeline result."""
    pipeline = result.get("pipeline", [])
    jf_data = result.get("data", {})
    in_library = jf_data.get("in_library", False)

    steps = []
    for step in pipeline:
        steps.append(Metric(label=step.replace("_", " ").title(), value="Done"))

    return Card(
        children=[
            Metric(label="Status", value="In Library" if in_library else "Queued"),
            Metric(label="Result", value=result.get("message", "")),
        ]
        + steps,
        title="Media Request Pipeline",
        badges=[Badge(label="Jellyfin" if in_library else "Arr Stack")],
    )


def build_stats_card(stats_data: dict[str, dict]) -> Card:
    """Build a consolidated stack statistics card."""
    data = stats_data.get("data", {})
    rows = []
    for name, info in data.items():
        if not info.get("enabled"):
            continue
        item_keys = [k for k in info if k not in ("enabled", "wanted", "error")]
        item_key = item_keys[0] if item_keys else "items"
        rows.append(
            Row(
                children=[
                    Metric(label="Service", value=name.title()),
                    Metric(label="Items", value=str(info.get(item_key, 0))),
                    Metric(label="Wanted", value=str(info.get("wanted", 0))),
                ]
            )
        )

    items_total = sum(
        int(info.get(next((k for k in info if k not in ("enabled", "wanted", "error")), "items"), 0))
        for info in data.values()
        if info.get("enabled")
    )
    wanted_total = sum(info.get("wanted", 0) for info in data.values() if info.get("enabled"))

    return Card(
        children=rows,
        title="*arr Stack Statistics",
        badges=[Badge(label=f"{items_total} items"), Badge(label=f"{wanted_total} wanted")],
    )
