
# LispBM Searchable Reference Manual

Searchable HTML reference manual built from Markdown source files.

Uses Pandoc to generate HTML from Markdown and Pagefind to build a search index.

## Updating the reference manual

From the `src/` directory:

1. Fetch the latest Markdown sources:
   ```
   bash fetch.sh
   ```
   This pulls documentation from the lispbm repo and VESC repos.

2. Build the HTML and search index:
   ```
   make
   ```
   Generated HTML and the Pagefind index are written to `html/`.

**Note:** Adding a new manual does not automatically add a reference card to
`src/index.html`. That card must be added manually.

