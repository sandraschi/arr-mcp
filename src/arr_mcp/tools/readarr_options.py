"""Read-only discovery of the user's Readarr add-book configuration choices."""

from __future__ import annotations

import asyncio

from arr_mcp.constants import TOOL_VERSION


def register_readarr_options(mcp, client) -> None:
    if client is None:
        return

    @mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False}, version=TOOL_VERSION)
    async def readarr_add_options() -> dict:
        """List root folders, quality profiles, metadata profiles and existing tags.

        Use the returned paths and IDs when calling readarr_add_book for a new
        author. These are author-level settings; existing authors retain their
        current configuration. This tool does not create tags or change settings.
        """
        try:
            roots, quality, metadata, tags = await asyncio.gather(
                client.get_root_folders(),
                client.get_quality_profiles(),
                client.get_metadata_profiles(),
                client.get_tags(),
            )
            # Root-folder resources may contain Calibre connection settings.
            # Return only UI choices, never the complete resource.
            root_keys = (
                "id", "name", "path", "freeSpace", "defaultQualityProfileId",
                "defaultMetadataProfileId", "defaultTags",
            )
            return {
                "success": True,
                "message": "Available Readarr settings for adding a book with a new author",
                "data": {
                    "root_folders": [{k: row[k] for k in root_keys if k in row} for row in roots],
                    "quality_profiles": [{"id": row["id"], "name": row["name"]} for row in quality],
                    "metadata_profiles": [{"id": row["id"], "name": row["name"]} for row in metadata],
                    "tags": [{"id": row["id"], "label": row["label"]} for row in tags],
                    "monitor_modes": ["specific_book", "all", "future", "missing", "existing", "first", "latest", "none"],
                    "monitor_new_books_modes": ["all", "none", "new"],
                },
            }
        except Exception:
            return {"success": False, "message": "Could not retrieve Readarr add options", "data": {}}
