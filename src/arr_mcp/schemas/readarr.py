"""Readarr response models — authors, books, editions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Author(BaseModel):
    """A Readarr author resource."""

    id: int | None = Field(default=None, description="Readarr author ID.")
    author_name: str = Field(default="", description="Author name.", alias="authorName")
    foreign_author_id: str | None = Field(default=None, description="Foreign author ID.", alias="foreignAuthorId")
    monitored: bool = Field(default=False, description="Whether monitored.")
    quality_profile_id: int | None = Field(default=None, description="Quality profile ID.", alias="qualityProfileId")
    path: str | None = Field(default=None, description="Filesystem path.")
    overview: str | None = Field(default=None, description="Author biography.")
    genres: list[str] = Field(default_factory=list, description="Genre list.")
    tags: list[int] = Field(default_factory=list, description="Tag IDs.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class Book(BaseModel):
    """A Readarr book resource."""

    id: int | None = Field(default=None, description="Book ID.")
    title: str = Field(default="", description="Book title.")
    author_id: int | None = Field(default=None, description="Parent author ID.", alias="authorId")
    foreign_book_id: str | None = Field(default=None, description="Foreign book ID.", alias="foreignBookId")
    isbn: str | None = Field(default=None, description="ISBN-13.")
    release_date: str | None = Field(default=None, description="Publication date.", alias="releaseDate")
    monitored: bool = Field(default=False, description="Whether monitored.")
    pages: int | None = Field(default=None, description="Page count.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class AuthorListResult(BaseModel):
    """Wrapper for author/book list responses."""

    success: bool = Field(description="Whether the operation succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    data: list[Author] | list[Book] | list[dict[str, Any]] = Field(default_factory=list)
    total: int | None = Field(default=None, description="Total count when applicable.")
