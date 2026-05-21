"""Readarr HTTP client (Books).

Extends :class:`BaseArrClient` with Readarr-specific endpoints for author
management, books, book files, and editions.
"""

from __future__ import annotations

from typing import Any

from arr_mcp.constants import DEFAULT_TIMEOUT, READARR_API_PATH
from arr_mcp.services.base import BaseArrClient


class ReadarrClient(BaseArrClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(
            name="Readarr",
            base_url=base_url,
            api_key=api_key,
            api_path=READARR_API_PATH,
            timeout=timeout,
        )

    # ── authors ───────────────────────────────────────────────────

    async def get_authors(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/author")  # type: ignore[return-value]

    async def get_author(self, author_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/author/{author_id}")  # type: ignore[return-value]

    async def lookup_author(self, term: str) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/author/lookup", term=term)  # type: ignore[return-value]

    async def add_author(
        self,
        foreign_author_id: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "foreignAuthorId": foreign_author_id,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
            **kwargs,
        }
        return await self._post(f"{self.api_path}/author", json=payload)

    async def delete_author(self, author_id: int, delete_files: bool = False) -> dict[str, Any]:
        return await self._delete(  # type: ignore[return-value]
            f"{self.api_path}/author/{author_id}",
            deleteFiles=delete_files,
        )

    async def update_author(self, author_id: int, **fields: Any) -> dict[str, Any]:
        author = await self.get_author(author_id)
        author.update(fields)
        return await self._put(f"{self.api_path}/author/{author_id}", json=author)

    # ── books ─────────────────────────────────────────────────────

    async def get_books(
        self,
        author_id: int | None = None,
        include_all_author_books: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if author_id:
            params["authorId"] = author_id
        params["includeAllAuthorBooks"] = include_all_author_books
        return await self._get(f"{self.api_path}/book", **params)  # type: ignore[return-value]

    async def get_book(self, book_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/book/{book_id}")  # type: ignore[return-value]

    async def lookup_book(self, term: str) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/book/lookup", term=term)  # type: ignore[return-value]

    async def update_book(self, book_id: int, **fields: Any) -> dict[str, Any]:
        book = await self.get_book(book_id)
        book.update(fields)
        return await self._put(f"{self.api_path}/book/{book_id}", json=book)

    async def set_books_monitored(self, book_ids: list[int], monitored: bool) -> dict[str, Any]:
        return await self._put(  # type: ignore[return-value]
            f"{self.api_path}/book/monitor",
            json={"bookIds": book_ids, "monitored": monitored},
        )

    async def delete_book(self, book_id: int, delete_files: bool = False) -> dict[str, Any]:
        return await self._delete(  # type: ignore[return-value]
            f"{self.api_path}/book/{book_id}",
            deleteFiles=delete_files,
        )

    # ── book files ────────────────────────────────────────────────

    async def get_book_files(
        self,
        author_id: int | None = None,
        book_id: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if author_id:
            params["authorId"] = author_id
        if book_id:
            params["bookId"] = book_id
        return await self._get(f"{self.api_path}/bookfile", **params)  # type: ignore[return-value]

    async def get_book_file(self, file_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/bookfile/{file_id}")  # type: ignore[return-value]

    async def delete_book_file(self, file_id: int) -> dict[str, Any]:
        return await self._delete(f"{self.api_path}/bookfile/{file_id}")  # type: ignore[return-value]
