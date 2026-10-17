# Readarr (Books) — arr-mcp service guide

Book collection manager. arr-mcp tools: `readarr_authors`
(list, lookup, get, add, delete, update), `readarr_books`
(list, get, lookup, set_monitored), plus `readarr_add_book`,
`readarr_delete_book`, `readarr_delete_books`, `readarr_add_options`.
Page: `/readarr`.

## Install

```bash
docker compose up -d readarr
# …or standalone (pinned build — upstream retired the floating tags)
docker run -d --name=readarr -p 8787:8787 \
  -v /path/to/config:/config -v /path/to/books:/books \
  lscr.io/linuxserver/readarr:amd64-develop-0.4.18.2805-ls157
```

First launch opens http://localhost:8787 — metadata comes from
Goodreads/Google Books.

## API key

Readarr UI → Settings → General → API Key.

## Connect to arr-mcp

```env
READARR_URL=http://localhost:8787
READARR_API_KEY=<paste-key>
READARR_ENABLED=true
```

## Common operations

```python
opts = readarr_add_options()                        # profiles, folders, tags
readarr_add_book(foreign_book_id="123", author_id=7)
readarr_delete_book(book_id=99)                     # dry-run preview first
readarr_delete_books(book_ids=[1, 2, 3], dry_run=False)
```

## Troubleshooting

- New-author adds need all four fields (foreign_author_id,
  quality/metadata profile ids, root folder) — or just pass `author_id`.
- Deletes never remove authors; `delete_files` needs its confirmation flag.
- Duplicates are refused by `foreign_book_id` with the existing record.
